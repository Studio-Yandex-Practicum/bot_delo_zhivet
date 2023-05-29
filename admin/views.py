from threading import Thread

import flask_admin
import flask_login as login
from flask import flash, redirect, render_template, request, url_for
from flask_admin import AdminIndexView, expose, helpers
from flask_admin.contrib import sqla
from flask_mail import Mail, Message
from flask_security import current_user
from sqlalchemy import select
from werkzeug.security import generate_password_hash

from src.core.db.model import (
    Assistance_disabled, Pollution, Staff, Tag_Assistance, Tag_Pollution, User,
    Volunteer,
)

from . import app
from .config import Config
from .database import db
from .forms import ForgotForm, LoginForm, PasswordResetForm, RegistrationForm
from .logger import get_logger
from .messages import (
    ALREADY_REGISTRED, BAD_TOKEN, MAIL_SEND_ERROR, MAIL_SEND_SUCCESS,
    PASSWORD_CHANGED_SUCCESS, RESET_PASSWORD_SUBJECT, RESTORE_PASSWORD_SEND,
    SUGGEST_REGISTRATION,
)
from .utils import (
    get_readonly_dict, get_reset_password_token, get_sortable_fields_list,
    get_table_fields_from_model, get_translated_lables,
    verify_reset_password_token,
)

logger = get_logger(__file__)


def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(staff_id):
        return db.session.query(Staff).get(staff_id)


init_login()

mail = Mail(app)


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            logger.info(MAIL_SEND_SUCCESS.format(subject=msg.subject, recipients=msg.recipients))
        except Exception as e:
            logger.error(
                MAIL_SEND_ERROR.format(
                    subject=msg.subject,
                    recipients=msg.recipients,
                    details=str(e),
                )
            )


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    token = get_reset_password_token(user)
    send_email(
        RESET_PASSWORD_SUBJECT,
        sender=Config.MAIL_USERNAME,
        recipients=[user.email],
        text_body=render_template("emails/reset_email.txt", user=user, token=token),
        html_body=render_template("emails/reset_email.html", user=user, token=token),
    )


class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for(".login_view"))
        return super(MyAdminIndexView, self).index()

    @expose("/login/", methods=("GET", "POST"))
    def login_view(self):
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for(".index"))
        link = SUGGEST_REGISTRATION.format(url=url_for(".register_view"))
        self._template_args["form"] = form
        self._template_args["link"] = link
        return super(MyAdminIndexView, self).index()

    @expose("/register/", methods=("GET", "POST"))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = Staff()

            form.populate_obj(user)
            user.password = generate_password_hash(form.password.data)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for(".index"))
        link = ALREADY_REGISTRED.format(url=url_for(".login_view"))
        self._template_args["form"] = form
        self._template_args["link"] = link
        return super(MyAdminIndexView, self).index()

    @expose("/logout/")
    def logout_view(self):
        login.logout_user()
        return redirect(url_for(".index"))

    @expose("/forgot_password/", methods=("GET", "POST"))
    def forgot_password_view(self):
        if login.current_user.is_authenticated:
            return redirect(url_for(".index"))
        form = ForgotForm(request.form)
        if helpers.validate_form_on_submit(form):
            staff = Staff.query.filter_by(email=form.email.data).first()
            if staff:
                send_password_reset_email(staff)
            flash(RESTORE_PASSWORD_SEND)
            return redirect(url_for(".login_view"))
        self._template_args["form"] = form
        self._template_args["link"] = "<p></p>"
        return super(MyAdminIndexView, self).index()

    @expose("/restore_password/<token>", methods=("GET", "POST"))
    def reset_password_view(self, token):
        if login.current_user.is_authenticated:
            return redirect(url_for(".index"))
        user = verify_reset_password_token(token)
        if not user:
            flash(BAD_TOKEN, "error")
            return redirect(url_for(".index"))
        form = PasswordResetForm(request.form)
        if helpers.validate_form_on_submit(form):
            user.set_password(form.password.data)
            db.session.merge(user)
            db.session.commit()
            flash(PASSWORD_CHANGED_SUCCESS)
            return redirect(url_for(".login_view"))
        self._template_args["form"] = form
        self._template_args["link"] = "<p>"
        return super(MyAdminIndexView, self).index()


class BaseModelView(sqla.ModelView):
    """Базовый вью-класс"""

    can_create = False
    can_delete = False
    page_size = 10

    def is_accessible(self):
        return (
            current_user.is_active
            and current_user.is_authenticated
            and (current_user.has_role("superuser") or current_user.has_role("admin"))
        )


class UserModelView(BaseModelView):
    """Вью-класс пользователей"""

    all_columns = get_table_fields_from_model(User)
    column_exclude_list = ("password",)
    form_excluded_columns = ("password",)
    column_labels = get_translated_lables(all_columns)
    form_columns = (
        "telegram_username",
        "is_banned",
    )
    form_widget_args = {"telegram_username": {"readonly": True}}
    column_searchable_list = ("telegram_username",)


class StaffModelView(BaseModelView):
    """Вью-класс администраторов"""

    all_columns = get_table_fields_from_model(Staff)
    column_exclude_list = ("password",)
    form_excluded_columns = ("password",)
    column_labels = get_translated_lables(all_columns)
    form_columns = (
        "login",
        "roles",
        "active",
    )
    form_widget_args = {"login": {"readonly": True}}

    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated and current_user.has_role("superuser")


class VolunteerModelView(BaseModelView):
    """Вью-класс волонтеров"""

    all_columns = get_table_fields_from_model(Volunteer)
    form_columns = (
        "telegram_username",
        "first_name",
        "last_name",
        "full_address",
        "birthday",
        "is_banned",
    )
    column_labels = get_translated_lables(all_columns)
    form_widget_args = get_readonly_dict(
        (
            "telegram_username",
            "first_name",
            "last_name",
            "full_address",
        )
    )
    column_exclude_list = ("geometry",)
    column_searchable_list = ("telegram_username",)


class AssistanceDisabledModelView(BaseModelView):
    """Вью-класс социальной помощи"""

    all_columns = get_table_fields_from_model(Assistance_disabled)
    column_labels = get_translated_lables(all_columns)
    sortable_relationship = {"tags": "tags.name"}
    column_sortable_list = get_sortable_fields_list(all_columns, sortable_relationship)
    column_filters = ("tags.name",)
    can_edit = False


class PolutionModelView(BaseModelView):
    """Вью-класс загрязнения"""

    all_columns = get_table_fields_from_model(Pollution)
    column_labels = get_translated_lables(all_columns)
    sortable_relationship = {"tags": "tags.name"}
    column_sortable_list = get_sortable_fields_list(all_columns, sortable_relationship)
    column_filters = ("tags.name",)
    can_edit = False


class TagPollutionModelView(BaseModelView):
    """Вью-класс тегов загрязнения."""

    all_columns = get_table_fields_from_model(Tag_Pollution)
    column_labels = get_translated_lables(all_columns)
    form_excluded_columns = ("created_at", "updated_at")
    can_edit = True
    can_create = True
    can_delete = True


class TagAssistanceModelView(BaseModelView):
    """Вью-класс тегов соц. помощи."""

    all_columns = get_table_fields_from_model(Tag_Assistance)
    column_labels = get_translated_lables(all_columns)
    form_excluded_columns = ("created_at", "updated_at")
    can_edit = True
    can_create = True
    can_delete = True


admin = flask_admin.Admin(
    app,
    "Бот «Дело живёт»",
    index_view=MyAdminIndexView(name="Главная"),
    base_template="my_master.html",
    template_mode=Config.BOOTSTRAP_VERSION,
)

admin.add_view(StaffModelView(Staff, db.session, name="Администраторы"))
admin.add_view(UserModelView(User, db.session, name="Пользователи"))

admin.add_view(VolunteerModelView(Volunteer, db.session, name="Волонтеры"))
admin.add_view(AssistanceDisabledModelView(Assistance_disabled, db.session, name="Социальная помощь"))
admin.add_view(PolutionModelView(Pollution, db.session, name="Загрязнения"))
admin.add_view(TagPollutionModelView(Tag_Pollution, db.session, name="Теги Загрязнения"))
admin.add_view(TagAssistanceModelView(Tag_Assistance, db.session, name="Теги Соц. помощи"))
