import os

import flask_login as login
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from src.core.db.db import Base_admin
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
Base_admin.query = db_session.query_property()
Base_admin.metadata.create_all(engine)
Session = sessionmaker(binds={Base_admin: engine})
session = Session()


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

from . import views


def build_sample_db():
    admin_role = Role(name='admin', description='admin')
    db.session.add(admin_role)
    db.session.commit()


if __name__ == '__main__':
    if not Role.query.filter_by(name='admin').all():
        with app.app_context():
            build_sample_db()
    app.run(debug=True)
