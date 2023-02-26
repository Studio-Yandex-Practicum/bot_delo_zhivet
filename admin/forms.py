from flask import Markup, url_for
from werkzeug.security import check_password_hash
from wtforms import fields, form, validators

from src.core.db.model import Staff

from .database import db
from .messages import (
    ACCOUNT_BUSY,
    ACCOUNT_LABEL,
    EMAIL_BUSY,
    EMAIL_LABEL,
    EMAIL_NOT_FOUND,
    INPUT_EMAIL,
    PASSWORD_LABEL,
    REPEAT_PASSWORD,
    WRONG_USER,
)


class LoginForm(form.Form):
    """Форма входа в админку"""

    login = fields.StringField(ACCOUNT_LABEL, validators=[validators.InputRequired()])
    password = fields.PasswordField(PASSWORD_LABEL, validators=[validators.InputRequired()])

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


class RegistrationForm(form.Form):
    """Форма регистрации"""

    login = fields.StringField(ACCOUNT_LABEL, validators=[validators.InputRequired()])
    email = fields.StringField(EMAIL_LABEL, validators=[validators.DataRequired(), validators.Email()])
    password = fields.PasswordField(PASSWORD_LABEL, validators=[validators.InputRequired(), validators.Length(min=8)])
    password2 = fields.PasswordField(
        REPEAT_PASSWORD, validators=[validators.DataRequired(), validators.EqualTo("password")]
    )

    def validate_login(self, field):
        if db.session.query(Staff).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError(ACCOUNT_BUSY)

    def validate_email(self, field):
        if db.session.query(Staff).filter_by(email=self.email.data).count() > 0:
            raise validators.ValidationError(EMAIL_BUSY)


class PasswordResetForm(form.Form):
    """Форма сброса пароля"""

    password = fields.PasswordField(PASSWORD_LABEL, validators=[validators.InputRequired(), validators.Length(min=8)])
    password2 = fields.PasswordField(
        REPEAT_PASSWORD, validators=[validators.DataRequired(), validators.EqualTo("password")]
    )


class ForgotForm(form.Form):
    """Форма 'Забыли пароль'"""

    email = fields.StringField(INPUT_EMAIL, validators=[validators.DataRequired(), validators.Email()])

    def validate_email(self, field):
        if db.session.query(Staff).filter_by(email=self.email.data).count() == 0:
            raise validators.ValidationError(EMAIL_NOT_FOUND)
