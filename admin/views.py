from threading import Thread

import flask_admin
import flask_login as login
from flask import flash, redirect, render_template, request, url_for
from flask_admin import AdminIndexView, expose, helpers
from flask_admin.contrib import sqla
from flask_mail import Mail, Message
from flask_security import current_user
from sqlalchemy import select
from structlog import get_logger
from werkzeug.security import generate_password_hash

from admin import app
from admin.config import settings
from admin.database import db
from admin.forms import (
    ForgotForm, LoginForm, PasswordResetForm, RegistrationForm,
)
from admin.messages import (
    ALREADY_REGISTRED, BAD_TOKEN, MAIL_SEND_ERROR, MAIL_SEND_SUCCESS,
    PASSWORD_CHANGED_SUCCESS, RESET_PASSWORD_SUBJECT, RESTORE_PASSWORD_SEND,
    SUGGEST_REGISTRATION,
)
from admin.utils import (
    check_tag_uniqueness, get_readonly_dict, get_reset_password_token,
    get_sortable_fields_list, get_table_fields_from_model,
    get_translated_lables, verify_reset_password_token,
)
from src.bot.tasks import (
    task_bulk_remove_assistance_tag_in_tracker,
    task_bulk_remove_pollution_tag_in_tracker,
    task_bulkupdate_and_remove_assistance_tag_in_tracker,
    task_bulkupdate_and_remove_pollution_tag_in_tracker,
)
from src.core.db.model import (
    Assistance_disabled, Pollution, Staff, Tag_Assistance, Tag_Pollution, User,
    Volunteer,
)

logger = get_logger("admin_logger")


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
            logger.info(MAIL_SEND_SUCCESS, subject=msg.subject, recipients=msg.recipients)
        except Exception as e:
            logger.error(MAIL_SEND_ERROR, subject=msg.subject, recipients=msg.recipients, details=str(e))


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    token = get_reset_password_token(user)
    send_email(
        RESET_PASSWORD_SUBJECT,
        sender=settings.MAIL_USERNAME,
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
    column_list = all_columns
    column_sortable_list = get_sortable_fields_list(all_columns, sortable_relationship)
    column_filters = ("tags.name",)
    can_edit = False


class PolutionModelView(BaseModelView):
    """Вью-класс загрязнения"""

    all_columns = get_table_fields_from_model(Pollution)
    column_labels = get_translated_lables(all_columns)
    sortable_relationship = {"tags": "tags.name"}
    column_list = all_columns
    column_sortable_list = get_sortable_fields_list(all_columns, sortable_relationship)
    column_filters = ("tags.name",)
    can_edit = False


class AbstractTagModelView(BaseModelView):
    """Абстрактный класс для наследования вью-классов тегов"""

    form_excluded_columns = ("created_at", "updated_at")
    can_edit = True
    can_create = True
    can_delete = True
    event_model = None  # This should be set in inheritor class

    def task_bulk_remove_event_tag_in_tracker(self, old_tag_name: str, event_ticket_ids: list[str]):
        """Этот метод должен быть переопределен в наследниках"""
        raise NotImplementedError()

    def task_bulkupdate_and_remove_event_tag_in_tracker(
        old_tag_name: str, new_tag_name: str, event_ticket_ids: list[str]
    ):
        """Этот метод должен быть переопределен в наследниках"""
        raise NotImplementedError()

    def on_model_change(self, form, model, is_created):
        if is_created:
            existing_tags = self.model.query.all()
            check_tag_uniqueness(model, existing_tags)
            return super().on_model_change(form, model, is_created)
        tag_beeing_changed = self.model.query.get(model.id)
        self.tag_beeing_changed = self.model(name=tag_beeing_changed.name, id=tag_beeing_changed.id)
        return super().on_model_change(form, model, is_created)

    def after_model_change(self, form, model, is_created):
        if is_created:
            return super().after_model_change(form, model, is_created)
        if self.event_model is None:
            raise NotImplementedError("'event_model' is not set")
        if self.tag_beeing_changed and self.tag_beeing_changed.id and model.id == self.tag_beeing_changed.id:
            stmt = select(self.event_model).where(self.event_model.tags.any(self.model.id == model.id))
            events = db.session.scalars(stmt).all()
            event_ticket_ids = [event.ticketID for event in events]

            self.task_bulkupdate_and_remove_event_tag_in_tracker(
                old_tag_name=self.tag_beeing_changed.name, new_tag_name=model.name, event_ticket_ids=event_ticket_ids
            )
        return super().after_model_change(form, model, is_created)

    def on_model_delete(self, model):
        stmt = select(self.event_model).where(self.event_model.tags.any(self.model.id == model.id))
        events = db.session.scalars(stmt).all()
        self.event_with_tag_to_delete_ticket_ids = [event.ticketID for event in events]

        return super().on_model_delete(model)

    def after_model_delete(self, model):
        if self.event_model is None:
            raise NotImplementedError("'event_model' is not set")

        self.task_bulk_remove_event_tag_in_tracker(
            old_tag_name=model.name, event_ticket_ids=self.event_with_tag_to_delete_ticket_ids
        )

        return super().after_model_delete(model)


class TagAssistanceModelView(AbstractTagModelView):
    """Вью-класс тегов соц. помощи."""

    all_columns = get_table_fields_from_model(Tag_Assistance)
    column_labels = get_translated_lables(all_columns)
    event_model = Assistance_disabled

    def task_bulkupdate_and_remove_event_tag_in_tracker(
        self, old_tag_name: str, new_tag_name: str, event_ticket_ids: list[str]
    ):
        task_bulkupdate_and_remove_assistance_tag_in_tracker.delay(old_tag_name, new_tag_name, event_ticket_ids)

    def task_bulk_remove_event_tag_in_tracker(self, old_tag_name: str, event_ticket_ids: list[str]):
        task_bulk_remove_assistance_tag_in_tracker.delay(old_tag_name, event_ticket_ids)


class TagPollutionModelView(AbstractTagModelView):
    """Вью-класс тегов загрязнения."""

    all_columns = get_table_fields_from_model(Tag_Pollution)
    column_labels = get_translated_lables(all_columns)
    event_model = Pollution

    def task_bulkupdate_and_remove_event_tag_in_tracker(
        self, old_tag_name: str, new_tag_name: str, event_ticket_ids: list[str]
    ):
        task_bulkupdate_and_remove_pollution_tag_in_tracker.delay(old_tag_name, new_tag_name, event_ticket_ids)

    def task_bulk_remove_event_tag_in_tracker(self, old_tag_name: str, event_ticket_ids: list[str]):
        task_bulk_remove_pollution_tag_in_tracker.delay(old_tag_name, event_ticket_ids)


admin = flask_admin.Admin(
    app,
    "Бот «Дело живёт»",
    index_view=MyAdminIndexView(name="Главная"),
    base_template="my_master.html",
    template_mode=settings.BOOTSTRAP_VERSION,
)

admin.add_view(StaffModelView(Staff, db.session, name="Администраторы"))
admin.add_view(UserModelView(User, db.session, name="Пользователи"))

admin.add_view(VolunteerModelView(Volunteer, db.session, name="Волонтеры"))
admin.add_view(AssistanceDisabledModelView(Assistance_disabled, db.session, name="Социальная помощь"))
admin.add_view(PolutionModelView(Pollution, db.session, name="Загрязнения"))
admin.add_view(TagPollutionModelView(Tag_Pollution, db.session, name="Теги Загрязнения"))
admin.add_view(TagAssistanceModelView(Tag_Assistance, db.session, name="Теги Соц. помощи"))
