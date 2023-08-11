from threading import Thread
from flask import flash, redirect, render_template, request, url_for
from flask_admin import AdminIndexView, expose, helpers
from werkzeug.security import generate_password_hash
import flask_login as login
from ..database import db
from flask_mail import Mail, Message
from .. import app
from structlog import get_logger
from ..config import settings

from ..forms.auth import (
    PasswordRecoveryForm,
    LoginForm,
    PasswordResetForm,
    RegistrationForm
)

from src.core.db.model import Staff

from ..messages import (
    BAD_TOKEN, MAIL_SEND_ERROR, MAIL_SEND_SUCCESS,
    PASSWORD_CHANGED_SUCCESS, RESET_PASSWORD_SUBJECT, RESTORE_PASSWORD_SEND,
)

from ..utils import (
    get_reset_password_token,
    verify_reset_password_token,
)


mail = Mail(app)

logger = get_logger("admin_logger")


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
    """ View главной страницы. """

    BUTTONS_TEXT = {
        'login_submit': 'Войти',
        'register_submit': 'Регистрация',
        'recovery_submit': 'Востановить пароль',
        'reset_submit': 'Сбросить пароль'
    }

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        form = LoginForm(request.form)
        user_by_login = form.get_user_by_login()

        if helpers.validate_form_on_submit(form):
            login.login_user(user_by_login)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))

        self._template_args['form'] = form
        self._template_args['registration_link'] = url_for('.register_view')
        self._template_args['submit_text'] = self.BUTTONS_TEXT['login_submit']

        return super(MyAdminIndexView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)

        if helpers.validate_form_on_submit(form):
            user = Staff()

            form.populate_obj(user)
            user.password = generate_password_hash(form.password.data)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)

            return redirect(url_for('.index'))

        self._template_args['form'] = form
        self._template_args['sigin_link'] = url_for('.login_view')
        self._template_args['submit_text'] = self.BUTTONS_TEXT['register_submit']

        return super(MyAdminIndexView, self).index()

    @expose("/logout/")
    def logout_view(self):
        login.logout_user()
        return redirect(url_for(".index"))

    @expose("/password_recovery/", methods=("GET", "POST"))
    def password_recovery_view(self):
        if login.current_user.is_authenticated:
            return redirect(url_for(".index"))

        form = PasswordRecoveryForm(request.form)

        if helpers.validate_form_on_submit(form):
            staff = Staff.query.filter_by(email=form.email.data).first()
            if staff:
                send_password_reset_email(staff)
            flash(RESTORE_PASSWORD_SEND)
            return redirect(url_for(".login_view"))

        self._template_args["form"] = form
        self._template_args['sigin_link'] = url_for('.login_view')
        self._template_args['submit_text'] = self.BUTTONS_TEXT['recovery_submit']

        return super(MyAdminIndexView, self).index()

    @expose("/password_reset/<token>", methods=("GET", "POST"))
    def password_reset_view(self, token):
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
        self._template_args['sigin_link'] = url_for('.login_view')
        self._template_args['submit_text'] = self.BUTTONS_TEXT['reset_submit']

        return super(MyAdminIndexView, self).index()
