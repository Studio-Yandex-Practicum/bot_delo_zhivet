import os

import flask_login as login
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from src.core.db.db import Base
from src.core.db.model import Role, Staff

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

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], pool_size=10000,
                       max_overflow=100)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base.query = db_session.query_property()
Base.metadata.create_all(engine)
Session = sessionmaker(binds={Base: engine})
session = Session()

if len(Staff.query.all()) < 1:
    staff = Staff(login='admin', email='admin@gmail.com',
                  password='pbkdf2:sha256:260000$UCyUKhCOz5sRuvUI$1772bcd9c97724ab4994d228ca77df5fd4ca341a6fba014074db39926c842f7b',
                  active=True)
    role = Role(name='superuser', description='superuser')
    role_admin = Role(name='admin', description='admin')
    staff.roles.append(role)
    db_session.add(staff)
    db_session.add(role)
    db_session.add(role_admin)
    db_session.commit()


def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(staff_id):
        return db.session.query(Staff).get(staff_id)


@app.route('/')
def index():
    return render_template('index.html')


init_login()

from . import views  # noqa


if __name__ == '__main__':
    app.run(debug=True)
