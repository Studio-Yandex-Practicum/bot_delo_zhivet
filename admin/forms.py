from werkzeug.security import check_password_hash
from wtforms import form, fields, validators

from . import db
from src.core.db.model import Staff


class LoginForm(form.Form):
    """Форма входа в админку"""
    login = fields.StringField(validators=[validators.InputRequired()])
    password = fields.PasswordField(validators=[validators.InputRequired()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(Staff).filter_by(login=self.login.data).first()


class RegistrationForm(form.Form):
    """Форма регистрации"""

    login = fields.StringField('Login', validators=[validators.InputRequired()])
    email = fields.StringField('Email', validators=[validators.DataRequired(), validators.Email()])
    password = fields.PasswordField('Password', validators=[validators.InputRequired(), validators.Length(min=8)])
    password2 = fields.PasswordField('Repeat password', validators=[
        validators.DataRequired(), validators.EqualTo('password')])

    def validate_login(self, field):
        if db.session.query(Staff).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('User with this login is already registered')

    def validate_email(self, field):
        if db.session.query(Staff).filter_by(email=self.email.data).count() > 0:
            raise validators.ValidationError(
                'User with this email is already registered')
