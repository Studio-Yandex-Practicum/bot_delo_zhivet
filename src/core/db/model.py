from sqlalchemy import (BigInteger, Boolean, Column, Date, DateTime, Float,
                        Table, ForeignKey, Integer, String, Text)

from flask_security import RoleMixin
from flask_login import UserMixin

from sqlalchemy.orm import relationship, backref
from werkzeug.security import check_password_hash, generate_password_hash

from src.core.db.db import Base, Base_admin


class User(Base):
    """Model User."""
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    is_banned = Column(Boolean, default=False)


class Volunteer(Base):
    """Model Volunteer."""
    telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
    city = Column(String(100), nullable=False)
    full_address = Column(Text, nullable=False)
    radius = Column(Integer, nullable=False)
    has_car = Column(Boolean, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    telegram_username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(13), unique=True, nullable=True)
    birthday = Column(Date, nullable=True)
    deleted_at = Column(DateTime(timezone=True))
    is_banned = Column(Boolean, default=False)
    ticketID = Column(Text, nullable=True)


class Pollution(Base):
    """Model Pollution. Инфо о загрязнении."""

    photo = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)
    telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
    ticketID = Column(Text, nullable=True)


class Assistance_disabled(Base):
    """Model Assistance_disabled. Инфо о помощи инвалиду."""

    city = Column(Text, nullable=False)
    full_address = Column(Text, nullable=False)
    comment = Column(Text, nullable=False)
    telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
    ticketID = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)


# Define models
roles_users = Table(
    'roles_users',
    Base_admin.metadata,
    Column('staff_id', Integer, ForeignKey('staff.id')),
    Column('role_id', Integer, ForeignKey('role.id'))
    # Column('staff_id', UUID(), ForeignKey('staff.id')),
    # Column('role_id', UUID(), ForeignKey('role.id'))
)


class Role(Base_admin, RoleMixin):
    name = Column(String, unique=True)
    description = Column(String(255))

    def __str__(self):
        return self.name


class Staff(Base_admin, UserMixin):
    # def createSession(self):
    #     Session = sessionmaker()
    #     self.session = Session.configure(bind=self.engine)
    first_name = Column(String(255))
    last_name = Column(String(255))
    login = Column(String(255), unique=True)
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
        return self.active

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
        return self.login

    #
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
