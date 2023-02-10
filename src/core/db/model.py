from flask_login import UserMixin
from flask_security import RoleMixin
from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship

from core.mixins import ExtraUserMixin
from src.core.db.db import Base


class User(Base):
    """Модель пользователя"""

    telegram_username = Column(String(100), nullable=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    is_banned = Column(Boolean, default=False)


class Volunteer(Base):
    """Модель волонтера"""

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
    """Модель сообщения о загрязнении"""

    photo = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)
    telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
    ticketID = Column(Text, nullable=True)


class Assistance_disabled(Base):
    """Модель сообщения о социальной помощи"""

    city = Column(Text, nullable=False)
    full_address = Column(Text, nullable=False)
    comment = Column(Text, nullable=False)
    telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
    ticketID = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)


roles_users = Table(
    "roles_users",
    Base.metadata,
    Column("staff_id", UUID(as_uuid=True), ForeignKey("staff.id")),
    Column("role_id", UUID(as_uuid=True), ForeignKey("role.id")),
)


class Role(Base, RoleMixin):
    """Модель роли для персонала"""

    name = Column(String, unique=True)
    description = Column(String(255))

    def __str__(self):
        return self.name


class Staff(Base, UserMixin, ExtraUserMixin):
    """Модель персонала"""

    first_name = Column(String(255))
    last_name = Column(String(255))
    login = Column(String(255), unique=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    active = Column(Boolean())
    roles = relationship("Role", secondary=roles_users, backref=backref("users", lazy="dynamic"))
