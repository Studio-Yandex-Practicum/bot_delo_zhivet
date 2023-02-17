import os.path as op

import flask_admin
import flask_login as login
from flask import redirect, request, url_for
from flask_admin import AdminIndexView, expose, helpers
from flask_admin.contrib import sqla
from flask_security import current_user
from werkzeug.security import generate_password_hash

from src.core.db.model import Staff, User

from . import app
from .database import db
from .forms import LoginForm, RegistrationForm


def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(staff_id):
        return db.session.query(Staff).get(staff_id)


init_login()


class MyModelView(sqla.ModelView):
    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated and current_user.has_role("admin")


class SuperuserModelView(sqla.ModelView):
    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated and current_user.has_role("superuser")


class MyAdminIndexView(AdminIndexView):

    endpoint = "/static"

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
        link = "<p>Don't have an account? <a href=\"" + url_for(".register_view") + '">Click here to register.</a></p>'
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
        link = '<p>Already have an account? <a href="' + url_for(".login_view") + '">Click here to log in.</a></p>'
        self._template_args["form"] = form
        self._template_args["link"] = link
        return super(MyAdminIndexView, self).index()

    @expose("/logout/")
    def logout_view(self):
        login.logout_user()
        return redirect(url_for(".index"))


admin = flask_admin.Admin(
    app,
    "Bot delo zhivet : Admin console",
    index_view=MyAdminIndexView(),
    base_template="my_master.html",
    template_mode="bootstrap4",
)

path = op.join(op.dirname(__file__), "static")
admin.add_view(MyModelView(User, db.session, name="User"))
admin.add_view(SuperuserModelView(Staff, db.session, name="Staff"))
