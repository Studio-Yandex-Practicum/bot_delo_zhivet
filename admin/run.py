from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)


from src.core.db.model import (Assistance_disabled, Member, Pollution,
                               Report, Request,
                               Shift, Task, User,
                               Volunteer)


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
admin.add_view(ModelView(Member, db.session, name='Member'))
admin.add_view(ModelView(Request, db.session, name='Request'))
admin.add_view(ModelView(Shift, db.session, name='Shift'))
admin.add_view(ModelView(Report, db.session, name='Report'))
admin.add_view(ModelView(Task, db.session, name='Task'))
admin.add_view(ModelView(Volunteer, db.session, name='Volunteer'))
admin.add_view(ModelView(Pollution, db.session, name='Pollution'))
admin.add_view(
    ModelView(Assistance_disabled, db.session, name='Assistance_disabled')
)

if __name__ == '__main__':
    app.run(debug=True)
