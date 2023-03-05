import re

from werkzeug.security import check_password_hash
from wtforms import fields, form, validators

from src.core.db.model import Staff

from .database import db
from .messages import (
    ACCOUNT_BUSY,
    ACCOUNT_LABEL,
    DISSALOWED_CHARS_IN_ACCOUNT,
    DISSALOWED_CHARS_IN_PASWORD,
    EMAIL_BUSY,
    EMAIL_LABEL,
    EMAIL_NOT_FOUND,
    INPUT_EMAIL,
    PASSWORD_CONTAINS_ACCOUNT,
    PASSWORD_LABEL,
    PASSWORD_TOO_LONG,
    REPEAT_PASSWORD,
    WRONG_PASSWORD,
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
            raise validators.ValidationError(WRONG_PASSWORD)

    def get_user(self):
        return db.session.query(Staff).filter_by(login=self.login.data).first()


class RegistrationForm(form.Form):
    """Форма регистрации"""

    login = fields.StringField(ACCOUNT_LABEL, validators=[validators.InputRequired(), validators.Length(min=1, max=20)])
    email = fields.StringField(EMAIL_LABEL, validators=[validators.DataRequired(), validators.Email()])
    password = fields.PasswordField(PASSWORD_LABEL, validators=[validators.InputRequired(), validators.Length(min=8)])
    password2 = fields.PasswordField(
        REPEAT_PASSWORD,
        validators=[validators.DataRequired(), validators.EqualTo("password"), validators.Length(min=8)],
    )

    def validate_login(self, field):
        if re.match(r"^[a-zA-Z]+$", self.login.data) is None:
            raise validators.ValidationError(DISSALOWED_CHARS_IN_ACCOUNT)
        if db.session.query(Staff).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError(ACCOUNT_BUSY)

    def validate_password(self, field):
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
