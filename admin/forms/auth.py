from flask import Markup, url_for
from werkzeug.security import check_password_hash
from wtforms import validators

from .common_fields import (
    LoginField,
    EmailField,
    PasswordField,
    PasswordRepeatField
)

from .constants import ERROR_MESSAGE


class LoginForm(LoginField, PasswordField):
    """ Форма входа в админку. """

    def validate_login(self, field):
        current_user = self.get_user_by_login()

        if current_user is None and not field.errors:
            raise validators.ValidationError(ERROR_MESSAGE['wrong_user'].format(field.data))

    def validate_password(self, field):
        user = self.get_user_by_login()

        if user is None:
            return

        password_hash = check_password_hash(user.password, field.data)

        if not password_hash and not field.errors:
            raise validators.ValidationError(
                Markup(ERROR_MESSAGE['incorrect_password'].format(url_for(".password_recovery_view")))
            )


class RegistrationForm(LoginField, PasswordField, PasswordRepeatField, EmailField):

    def validate_login(self, field):
        user = self.get_user_by_login()

        if user is not None and not field.errors:
            raise validators.ValidationError(ERROR_MESSAGE['login_busy'])

    def validate_email(self, field):
        user = self.get_user_by_email()

        if user is not None and not field.errors:
            raise validators.ValidationError(ERROR_MESSAGE['email_busy'])

    def validate_password(self, field):
        if field.data.lower() == self.login.data.lower():
            raise validators.ValidationError(ERROR_MESSAGE['should_not_match'])


class PasswordResetForm(PasswordField, PasswordRepeatField):
    """
    Форма сброса пароля.
    Страница формируется по токену.
    """
    pass


class PasswordRecoveryForm(EmailField):
    """ Форма востановления пароля. """

    def validate_email(self, field):
        user = self.get_user_by_email()

        if user is None and not field.errors:
            raise validators.ValidationError(ERROR_MESSAGE['email_busy'])
