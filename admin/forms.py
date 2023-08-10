import re

from flask import Markup, url_for
from werkzeug.security import check_password_hash
from wtforms import fields, form, validators

from admin.database import db
from admin.messages import (
    ACCOUNT_BUSY, ACCOUNT_LABEL, DISSALOWED_CHARS_IN_ACCOUNT,
    DISSALOWED_CHARS_IN_PASWORD, EMAIL_BUSY, EMAIL_LABEL, EMAIL_NOT_FOUND,
    EQUAL_PASSWORDS, INPUT_EMAIL, INVALID_EMAIL, LOGIN_LENGTH,
    PASSWORD_CONTAINS_ACCOUNT, PASSWORD_LABEL, PASSWORD_LENGTH,
    PASSWORD_TOO_LONG, REPEAT_PASSWORD, REQUIRED_FIELD, WRONG_USER,
)
from src.core.db.model import Staff


class BaseForm(form.Form):
    """Объект класса Form с отключенной браузерной валидацией полей."""

    class Meta:
        def render_field(self, field, render_kw):
            render_kw.setdefault("required", False)
            return super().render_field(field, render_kw)


class LoginForm(BaseForm):
    """Форма входа в админку"""

    login = fields.StringField(ACCOUNT_LABEL, validators=[validators.InputRequired(REQUIRED_FIELD)])
    password = fields.PasswordField(PASSWORD_LABEL, validators=[validators.InputRequired(REQUIRED_FIELD)])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError(WRONG_USER)

        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError(
                Markup(
                    "Неверный пароль"
                    '<p>Забыли пароль? <a href="'
                    + url_for(".forgot_password_view")
                    + '">Нажмите здесь, чтобы восстановить его</a></p>'
                )
            )

    def get_user(self):
        return db.session.query(Staff).filter_by(login=self.login.data).first()


class RegistrationForm(BaseForm):
    """Форма регистрации"""

    login = fields.StringField(ACCOUNT_LABEL, validators=[validators.InputRequired(REQUIRED_FIELD)])
    email = fields.StringField(
        EMAIL_LABEL, validators=[validators.DataRequired(EMAIL_LABEL), validators.Email(INVALID_EMAIL)]
    )
    password = fields.PasswordField(PASSWORD_LABEL, validators=[validators.InputRequired(REQUIRED_FIELD)])
    password2 = fields.PasswordField(
        REPEAT_PASSWORD,
        validators=[
            validators.DataRequired(REQUIRED_FIELD),
            validators.EqualTo("password", message=EQUAL_PASSWORDS),
        ],
    )

    def validate_login(self, field):
        if re.match(r"^[a-zA-Z]+$", self.login.data) is None:
            raise validators.ValidationError(DISSALOWED_CHARS_IN_ACCOUNT)
        if db.session.query(Staff).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError(ACCOUNT_BUSY)
        if len(self.login.data) > 20:
            raise validators.ValidationError(LOGIN_LENGTH)

    def validate_password(self, field):
        if len(self.password.data) < 8:
            raise validators.ValidationError(PASSWORD_LENGTH)
        # Использование свойства max во встроенном валидаторе длины может сказаться на
        # пользовательском опыте. Например, человек, может набрать пароль 25 символов,
        # но при валидации через max оставшиеся 5 символов будут просто обрезаны
        # без каких-либо сообщений для пользователя
        if len(self.password.data) > 20:
            raise validators.ValidationError(PASSWORD_TOO_LONG.format(max_len=20))
        if self.password.data.lower().find(self.login.data.lower()) != -1:
            raise validators.ValidationError(PASSWORD_CONTAINS_ACCOUNT)
        if re.findall(r"[\s\t]", self.password.data):
            raise validators.ValidationError(DISSALOWED_CHARS_IN_PASWORD)

    def validate_password2(self, field):
        if len(self.password2.data) < 8:
            raise validators.ValidationError(PASSWORD_LENGTH)

    def validate_email(self, field):
        if db.session.query(Staff).filter_by(email=self.email.data).count() > 0:
            raise validators.ValidationError(EMAIL_BUSY)


class PasswordResetForm(BaseForm):
    """Форма сброса пароля"""

    password = fields.PasswordField(PASSWORD_LABEL, validators=[validators.InputRequired(REQUIRED_FIELD)])
    password2 = fields.PasswordField(
        REPEAT_PASSWORD,
        validators=[validators.DataRequired(REQUIRED_FIELD), validators.EqualTo("password", message=EQUAL_PASSWORDS)],
    )

    def validate_password(self, field):
        if len(self.password.data) < 8:
            raise validators.ValidationError(PASSWORD_LENGTH)

    def validate_password2(self, field):
        if len(self.password2.data) < 8:
            raise validators.ValidationError(PASSWORD_LENGTH)


class ForgotForm(BaseForm):
    """Форма 'Забыли пароль'"""

    email = fields.StringField(
        INPUT_EMAIL, validators=[validators.DataRequired(REQUIRED_FIELD), validators.Email(INVALID_EMAIL)]
    )

    def validate_email(self, field):
        if db.session.query(Staff).filter_by(email=self.email.data).count() == 0:
            raise validators.ValidationError(EMAIL_NOT_FOUND)
