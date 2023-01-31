from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, \
    Text, BigInteger, Float, Table, Boolean
from flask_security import (Security, SQLAlchemyUserDatastore,
                            UserMixin, RoleMixin, login_required, current_user
                            )
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import check_password_hash, generate_password_hash
from admin.app import db, login_manager

from src.core.db.db import Base


# class User(Base):
#     """Model User."""
#     telegram_id = Column(BigInteger, unique=True, nullable=False)
#
#
# class Volunteer(Base):
#     """Model Volunteer."""
#     telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
#     name = Column(String(100), nullable=True)
#     city = Column(String(100), nullable=False)
#     phone = Column(String(13), unique=True, nullable=True)
#     radius = Column(Text, nullable=False)
#     has_car = Column(Text, nullable=False)
#     birthday = Column(Date, nullable=True)
#     deleted_at = Column(DateTime(timezone=True))
#
#
# class Pollution(Base):
#     """Model Pollution. Инфо о загрязнении."""
#
#     photo = Column(String(100), nullable=False)
#     latitude = Column(Float, nullable=False)
#     longitude = Column(Float, nullable=False)
#     comment = Column(Text, nullable=True)
#     telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
#     ticketID = Column(BigInteger, nullable=True)


# class Assistance_disabled(Base):
#     """Model Assistance_disabled. Инфо о помощи инвалиду."""
#
#     city = Column(Text, nullable=False)
#     street = Column(Text, nullable=False)
#     house = Column(Text, nullable=False)
#     comment = Column(Text, nullable=False)
#     telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
#     ticketID = Column(Integer, nullable=True)
#     latitude = Column(Integer, nullable=True)
#     longitude = Column(Integer, nullable=True)


# # Define models
# roles_users = Table(
#     'roles_users',
#     Base.metadata,
#     Column('staff_id', UUID(), ForeignKey('staff.id')),
#     Column('role_id', UUID(), ForeignKey('role.id'))
# )
#
#
# class Role(Base, RoleMixin):
#     name = Column(String, unique=True)
#     description = Column(String(255))
#
#     def __str__(self):
#         return self.name
#
#
# class Staff(Base, UserMixin):
#
#     def createSession(self):
#         Session = sessionmaker()
#         self.session = Session.configure(bind=self.engine)
#
#     name = Column(String(255))
#     username = Column(String(255), unique=True)
#     email = Column(String(255), unique=True)
#     password = Column(String(255))
#     active = Column(Boolean())
#     roles = relationship('Role', secondary=roles_users,
#                          backref=backref('users', lazy='dynamic'))
#
#     # Flask - Login
#     @property
#     def is_authenticated(self):
#         return True
#
#     @property
#     def is_active(self):
#         return True
#
#     @property
#     def is_anonymous(self):
#         return False
#
#     # Flask-Security
#     def has_role(self, *args):
#         return set(args).issubset({role.name for role in self.roles})
#
#     def get_id(self):
#         return self.id
#
#     # Required for administrative interface
#     def __unicode__(self):
#         return self.username
#
#     def set_password(self, password):
#         self.password = generate_password_hash(password)
#
#     def check_password(self, password):
#         return check_password_hash(self.password, password)


# Отвечает за сессию пользователей. Запрещает доступ к роутам, перед которыми указано @login_required
# @login_manager.user_loader
# def load_user(user_id):
#     return session.query(User).get(user_id)
#
#     def __str__(self):
#         return self.email



roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))
)


class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    # Нужен для security!
    active = db.Column(db.Boolean())
    # Для получения доступа к связанным объектам
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    # Flask - Login
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    # Flask-Security
    def has_role(self, *args):
        return set(args).issubset({role.name for role in self.roles})

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# Отвечает за сессию пользователей. Запрещает доступ к роутам, перед которыми указано @login_required
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)