from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, \
    Text, BigInteger, Float, Table, Boolean
from flask_security import (Security, SQLAlchemyUserDatastore,
                            RoleMixin, login_required, current_user
                            )
from flask_login import UserMixin

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import check_password_hash, generate_password_hash
# from admin.app import login_manager, db

from src.core.db.db import Base


# class User(Base):
#     """Model User."""
#     telegram_id = Column(BigInteger, unique=True, nullable=False)


class Volunteer(Base):
    """Model Volunteer."""
    # telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
    name = Column(String(100), nullable=True)
    city = Column(String(100), nullable=False)
    phone = Column(String(13), unique=True, nullable=True)
    radius = Column(Text, nullable=False)
    has_car = Column(Text, nullable=False)
    birthday = Column(Date, nullable=True)
    deleted_at = Column(DateTime(timezone=True))


class Pollution(Base):
    """Model Pollution. Инфо о загрязнении."""

    photo = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)
    # telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
    ticketID = Column(BigInteger, nullable=True)


class Assistance_disabled(Base):
    """Model Assistance_disabled. Инфо о помощи инвалиду."""

    city = Column(Text, nullable=False)
    street = Column(Text, nullable=False)
    house = Column(Text, nullable=False)
    comment = Column(Text, nullable=False)
    # telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
    ticketID = Column(Integer, nullable=True)
    latitude = Column(Integer, nullable=True)
    longitude = Column(Integer, nullable=True)


# Define models
roles_users = Table(
    'roles_users',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('role_id', Integer, ForeignKey('role.id'))
    # Column('staff_id', UUID(), ForeignKey('staff.id')),
    # Column('role_id', UUID(), ForeignKey('role.id'))
)


class Role(Base, RoleMixin):
    name = Column(String, unique=True)
    description = Column(String(255))

    def __str__(self):
        return self.name


class User(Base, UserMixin):

    def createSession(self):
        Session = sessionmaker()
        self.session = Session.configure(bind=self.engine)

    name = Column(String(255))
    username = Column(String(255), unique=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    active = Column(Boolean())
    # confirmed_at = Column(DateTime())
    roles = relationship('Role', secondary=roles_users,
                         backref=backref('users', lazy='dynamic'))

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


# # Отвечает за сессию пользователей. Запрещает доступ к роутам, перед которыми указано @login_required
# @login_manager.user_loader
# def load_user(user_id):
#     return db.session.query(User).get(user_id)
#
#     def __str__(self):
#         return self.email
