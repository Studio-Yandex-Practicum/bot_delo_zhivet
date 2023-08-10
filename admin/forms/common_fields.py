from wtforms import fields, form
from wtforms.fields import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Length, DataRequired, Email, EqualTo, Regexp

from ..database import db
from src.core.db.model import Staff

from .constants import (
    MIN_LENGTH_LOGIN,
    MAX_LENGTH_LOGIN,
    MIN_LENGTH_PASSWORD,
    MAX_LENGTH_PASSWORD,
    LABEL_FIELDS,
    ERROR_MESSAGE
)


class LoginField(form.Form):
    login = StringField(
        LABEL_FIELDS['login'],
        validators=[
            Regexp(r"^[a-zA-Z\d]+$", message='Только латинские буквы алфавита и цифры'),
            InputRequired(ERROR_MESSAGE['required_field']),
            Length(min=MIN_LENGTH_LOGIN,
                   max=MAX_LENGTH_LOGIN,
                   message=ERROR_MESSAGE['min_length_login'])])

    def get_user_by_login(self):
        """ Получить пользователя по полю login. """
        return db.session.query(Staff).filter_by(login=self.login.data).first()


class EmailField(form.Form):
    email = EmailField(
        LABEL_FIELDS['email'],
        validators=[
            DataRequired(ERROR_MESSAGE['required_field']),
            Email(ERROR_MESSAGE['incorrect_email'])])

    def get_user_by_email(self):
        """ Получить пользователя по полю email. """
        return db.session.query(Staff).filter_by(email=self.email.data).first()


class PasswordField(form.Form):
    password = PasswordField(
        LABEL_FIELDS['password'],
        validators=[
            Regexp(r"^[a-zA-Z\d]+[!@#$%^&*]*$", message='Только латинские буквы алфавита, цифры и символы !@#$%^&*'),
            DataRequired(ERROR_MESSAGE['required_field']),
            Length(min=MIN_LENGTH_PASSWORD,
                   max=MAX_LENGTH_PASSWORD,
                   message=ERROR_MESSAGE['min_length_password'])])


class PasswordRepeatField(form.Form):
    password_repeat = fields.PasswordField(
        LABEL_FIELDS['password_repeat'],
        validators=[
            Regexp(r"^[a-zA-Z\d]+[!@#$%^&*]*$", message='Только латинские буквы алфавита, цифры и символы !@#$%^&*'),
            DataRequired(ERROR_MESSAGE['required_field']),
            EqualTo('password', message=ERROR_MESSAGE['equal_passwords']),
            Length(min=MIN_LENGTH_PASSWORD,
                   max=MAX_LENGTH_PASSWORD,
                   message=ERROR_MESSAGE['min_length_password'])])
