from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

from src.core.db.model import (User, Member, Request,
                               Shift, Report, Task,
                               Volunteer, Pollution, Assistance_disabled)
from src.core.db.db import database_url


app = Flask(__name__)
app.config['FLASK_ENV'] = 'development'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


# class URLMap(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     original = db.Column(db.String(256), nullable=False)
#     short = db.Column(db.String(16), unique=True, nullable=False)


admin = Admin(app, name='bot_delo_zhivet', template_mode='bootstrap3')
# admin.add_view(ModelView(URLMap, db.session, name='URLMap'))

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
    # db.create_all()
    app.run(debug=True)