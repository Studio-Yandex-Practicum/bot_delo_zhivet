import flask_admin
from flask import abort, Flask, render_template, redirect, url_for, request
from flask_admin import Admin, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_security import (Security, SQLAlchemyUserDatastore,
                            UserMixin, RoleMixin, login_required, current_user,
                            RegisterForm
                            )
from flask_admin import helpers as admin_helpers
import flask_login as login

from dotenv import load_dotenv
import os

from src.core.db.model import (Assistance_disabled, Pollution,
                               User, Volunteer, Role, roles_users)

load_dotenv()

app = Flask(__name__)
app.secret_key = 'xxxxyyyyyzzzzz'


app.config['FLASK_ENV'] = 'development'
app.config.from_pyfile('config.py')

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('POSTGRES_DB')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Ставим редирект, если пользователь не авторизован, для страниц где обязательна авторизация
login_manager = LoginManager(app)
login_manager.login_view = 'admin_blueprint.login'

# # Define models
# roles_users = db.Table(
#     'roles_users',
#     db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
#     db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
# )
#
#
# class Role(db.Model, RoleMixin):
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(80), unique=True)
#     description = db.Column(db.String(255))
#
#     def __str__(self):
#         return self.name
#
#
# class Staff(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(255))
#     last_name = db.Column(db.String(255))
#     email = db.Column(db.String(255), unique=True)
#     password = db.Column(db.String(255))
#     active = db.Column(db.Boolean())
#     confirmed_at = db.Column(db.DateTime())
#     roles = db.relationship('Role', secondary=roles_users,
#                             backref=db.backref('users', lazy='dynamic'))
#
#     def __str__(self):
#         return self.email


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Create customized model view class
class MyModelView(ModelView):
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated and
                current_user.has_role('admin')
                )

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


# Переадресация страниц (используется в шаблонах)
class MyAdminIndexView(flask_admin.AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_page'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_page(self):
        if current_user.is_authenticated:
            return redirect(url_for('.index'))
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_page(self):
        login.logout_user()
        return redirect(url_for('.index'))

    @expose('/reset/')
    def reset_page(self):
        return redirect(url_for('.index'))





# Flask views
@app.route('/')
def index():
    return render_template('index.html')


# Create admin
# admin = flask_admin.Admin(app, base_template='admin/master-extended.html')
admin = flask_admin.Admin(app, index_view=MyAdminIndexView(), base_template='admin/master-extended.html')

# admin = flask_admin.Admin(
#     app,
#     'Example: Auth',
#     base_template='my_master.html',
#     template_mode='bootstrap4',
# )

# admin = Admin(app, name='bot_delo_zhivet', template_mode='bootstrap3')

# admin.add_view(ModelView(Staff, db.session, name='Staff'))
admin.add_view(MyModelView(Role, db.session, name='Role'))
# admin.add_view(ModelView(roles_users, db.session, name='roles_users'))


admin.add_view(ModelView(User, db.session, name='User'))
admin.add_view(ModelView(Volunteer, db.session, name='Volunteer'))
admin.add_view(ModelView(Pollution, db.session, name='Pollution'))
admin.add_view(
    ModelView(Assistance_disabled, db.session, name='Assistance_disabled')
)


# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True)
