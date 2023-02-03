import flask_admin
from flask import abort, Flask, render_template, redirect, url_for, request
from flask_admin import Admin, expose, helpers, AdminIndexView
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_security import (Security, SQLAlchemyUserDatastore,
                            current_user,
                            RegisterForm
                            )
from flask_admin import helpers as admin_helpers
import flask_login as login

from dotenv import load_dotenv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import form, fields, validators


from src.core.db.db import Base
from src.core.db.model import (Assistance_disabled, Pollution,
                               Volunteer, Role, User, roles_users)


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


engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], pool_size=10000, max_overflow=100)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base.query = db_session.query_property()
Base.metadata.create_all(engine)
Session = sessionmaker(binds={Base: engine})
# Session = sessionmaker(bind=engine)
session = Session()


# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.InputRequired()])
    password = fields.PasswordField(validators=[validators.InputRequired()])

    # def validate(self, extra_validators=None):
    #     initial_validation = super(RegisterForm, self).validate(
    #         extra_validators)
    #     if not initial_validation:
    #         return False
    #     user = User.query.filter_by(email=self.email.data).first()
    #     if user:
    #         self.email.errors.append("Email already registered")
    #         return False
    #     if self.password.data != self.confirm.data:
    #         self.password.errors.append("Passwords must match")
    #         return False
    #     return True

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password, self.password.data):
        # to compare plain text passwords use
        # if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(login=self.login.data).first()


class RegistrationForm(form.Form):
    login = fields.StringField(validators=[validators.InputRequired()])
    email = fields.StringField()
    password = fields.PasswordField(validators=[validators.InputRequired()])

    def validate_login(self, field):
        if db.session.query(User).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)



# # Ставим редирект, если пользователь не авторизован, для страниц где обязательна авторизация
# login_manager = LoginManager(app)
# login_manager.login_view = 'admin_blueprint.login'
#
# # Отвечает за сессию пользователей. Запрещает доступ к роутам, перед которыми указано @login_required
# @login_manager.user_loader
# def load_user(user_id):
#     return db.session.query(User).get(user_id)
#
#     def __str__(self):
#         return self.email

# # Setup Flask-Security
# user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# security = Security(app, user_datastore)

# from wtforms import StringField, SubmitField, TextAreaField,  BooleanField, PasswordField
#
#
# class LoginForm(FlaskForm):
#     username = StringField("Username", validators=[DataRequired()])
#     password = PasswordField("Password", validators=[DataRequired()])
#     remember = BooleanField("Remember Me")
#     submit = SubmitField()
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
# from admin.app import login_manager, db
#
#
# # Отвечает за сессию пользователей. Запрещает доступ к роутам, перед которыми указано @login_required
# @login_manager.user_loader
# def load_user(user_id):
#     return db.session.query(User).get(user_id)
#
#     def __str__(self):
#         return self.email





# # Create customized model view class
# class MyModelView(ModelView):
#     def is_accessible(self):
#         return (current_user.is_active and
#                 current_user.is_authenticated and
#                 current_user.has_role('admin')
#                 )
#
#     def _handle_view(self, name, **kwargs):
#         """
#         Override builtin _handle_view in order to redirect users when a view is not accessible.
#         """
#         if not self.is_accessible():
#             if current_user.is_authenticated:
#                 # permission denied
#                 abort(403)
#             else:
#                 # login
#                 return redirect(url_for('security.login', next=request.url))
#
#
# # Переадресация страниц (используется в шаблонах)
# class MyAdminIndexView(flask_admin.AdminIndexView):
#     @expose('/')
#     def index(self):
#         if not current_user.is_authenticated:
#             return redirect(url_for('.login_page'))
#         return super(MyAdminIndexView, self).index()
#
#     @expose('/login/', methods=('GET', 'POST'))
#     def login_page(self):
#         if current_user.is_authenticated:
#             return redirect(url_for('.index'))
#         return super(MyAdminIndexView, self).index()
#
#     @expose('/logout/')
#     def logout_page(self):
#         login.logout_user()
#         return redirect(url_for('.index'))
#
#     @expose('/reset/')
#     def reset_page(self):
#         return redirect(url_for('.index'))

# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated


# Create customized index view class that handles login & registration
class MyAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User()

            form.populate_obj(user)
            # we hash the users password to avoid saving it as plaintext in the db,
            # remove to use plain text:
            user.password = generate_password_hash(form.password.data)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))




# Flask views
@app.route('/')
def index():
    return render_template('index.html')

# # Setup Flask-Security
# user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# security = Security(app, user_datastore)


# Initialize flask-login
init_login()


# Create admin
# admin = flask_admin.Admin(app, base_template='admin/master-extended.html')
# admin = flask_admin.Admin(app, index_view=MyAdminIndexView(), base_template='admin/master-extended.html')

# Create admin
admin = flask_admin.Admin(app, 'Example: Auth', index_view=MyAdminIndexView(), base_template='my_master.html', template_mode='bootstrap4')

# admin = flask_admin.Admin(
#     app,
#     'Example: Auth',
#     base_template='my_master.html',
#     template_mode='bootstrap4',
# )

# admin = Admin(app, name='bot_delo_zhivet', template_mode='bootstrap3')

# admin.add_view(ModelView(Staff, db.session, name='Staff'))
admin.add_view(ModelView(Role, db.session, name='Role'))
# admin.add_view(ModelView(roles_users, db.session, name='roles_users'))


admin.add_view(ModelView(User, db.session, name='User'))
admin.add_view(MyModelView(Volunteer, db.session, name='Volunteer'))
admin.add_view(ModelView(Pollution, db.session, name='Pollution'))
admin.add_view(
    ModelView(Assistance_disabled, db.session, name='Assistance_disabled')
)



# define a context processor for merging flask-admin's template context into the
# flask-security views.
# @security.context_processor
# def security_context_processor():
#     return dict(
#         admin_base_template=admin.base_template,
#         admin_view=admin.index_view,
#         h=admin_helpers,
#         get_url=url_for
#     )

if __name__ == '__main__':
    # app.secret_key = os.urandom(24)
    app.run(debug=True)
