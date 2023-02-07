import flask_admin
import flask_login as login
from flask import redirect, url_for, request
from flask_admin import expose, helpers, AdminIndexView
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import ModelView
from flask_security import current_user
from werkzeug.security import generate_password_hash

from src.core.db.model import (Assistance_disabled, Pollution,
                               Volunteer, Role, Staff, User)
from . import app, db
from .forms import LoginForm, RegistrationForm


class MyModelView(sqla.ModelView):

    def is_accessible(self):
        return (current_user.is_active
                and current_user.is_authenticated
                and current_user.has_role('admin'))


class MyAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for(
            '.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
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
        link = '<p>Already have an account? <a href="' + url_for(
            '.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


admin = flask_admin.Admin(app, 'Example: Auth', index_view=MyAdminIndexView(),
                          base_template='my_master.html',
                          template_mode='bootstrap4')

if Staff.query.filter_by(login='admin').all():
    admin.add_view(MyModelView(Staff, db.session, name='Staff'))
if not Staff.query.filter_by(login='admin').all():
    admin.add_view(ModelView(Staff, db.session, name='Staff'))

admin.add_view(MyModelView(Role, db.session, name='Role'))
admin.add_view(MyModelView(User, db.session, name='User'))
admin.add_view(MyModelView(Volunteer, db.session, name='Volunteer'))
admin.add_view(MyModelView(Pollution, db.session, name='Pollution'))
admin.add_view(
    MyModelView(Assistance_disabled, db.session, name='Assistance_disabled')
)


def build_sample_db():
    admin_role = Role(name='admin', description='admin')
    db.session.add(admin_role)
    db.session.commit()
    if not Role.query.filter_by(name='admin').all():
        with app.app_context():
            build_sample_db()
