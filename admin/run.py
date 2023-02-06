from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv
import os

from src.core.db.model import (Assistance_disabled, Pollution,
                               User, Volunteer)

load_dotenv()

app = Flask(__name__)
app.config['FLASK_ENV'] = 'development'

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('POSTGRES_DB')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

admin = Admin(app, name='bot_delo_zhivet', template_mode='bootstrap3')

admin.add_view(ModelView(User, db.session, name='User'))
admin.add_view(ModelView(Volunteer, db.session, name='Volunteer'))
admin.add_view(ModelView(Pollution, db.session, name='Pollution'))
admin.add_view(
    ModelView(Assistance_disabled, db.session, name='Assistance_disabled')
)

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True)
