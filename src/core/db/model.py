from flask_login import UserMixin
from flask_security import RoleMixin
from geoalchemy2.types import Geography
from sqlalchemy import (
    TIMESTAMP, BigInteger, Boolean, Column, Date, DateTime, Float, ForeignKey,
    Integer, String, Table, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, backref, relationship
from werkzeug.security import check_password_hash, generate_password_hash

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
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    geometry = Column(Geography(geometry_type="POINT", srid=4326, dimension=2))
    telegram_username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(13), nullable=True)
    birthday = Column(Date, nullable=True)
    deleted_at = Column(DateTime(timezone=True))
    is_banned = Column(Boolean, default=False)
    ticketID = Column(Text, nullable=True)
    holiday_start = Column(TIMESTAMP, nullable=True)
    holiday_end = Column(TIMESTAMP, nullable=True)
    is_active = Column(Boolean, default=False)


class AbstractTag(Base):
    """Абстрактная модель тега."""

    __abstract__ = True
    name = Column(String(35), nullable=False, unique=True)
    priority = Column(Integer, nullable=True)

    def __str__(self):
        return self.name


class Tag_Pollution(AbstractTag):
    """Модель тега для сообщения о загрязнении."""

    pass


class Tag_Assistance(AbstractTag):
    """Модель тега для сообщения о социальной помощи."""

    pass


pollution_tag_connection = Table(
    "pollution_tag_connection",
    Base.metadata,
    Column("pollution_id", ForeignKey("pollution.id", ondelete="CASCADE")),
    Column("tag", ForeignKey("tag_pollution.id", ondelete="CASCADE")),
)
assistance_tag_connection = Table(
    "assistance_tag_connection",
    Base.metadata,
    Column("Assistance_id", ForeignKey("assistance_disabled.id", ondelete="CASCADE")),
    Column("tag", ForeignKey("tag_assistance.id", ondelete="CASCADE")),
)


class Pollution(Base):
    """Модель сообщения о загрязнении"""

    photo = Column(String(), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    geometry = Column(Geography(geometry_type="POINT", srid=4326, dimension=2))
    comment = Column(Text, nullable=True)
    telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
    ticketID = Column(Text, nullable=True)
    tags: Mapped[list[Tag_Pollution]] = relationship(
        argument=Tag_Pollution, secondary=pollution_tag_connection, lazy="subquery"
    )
    sender = relationship(User, lazy="subquery")


class Assistance_disabled(Base):
    """Модель сообщения о социальной помощи"""

    city = Column(Text, nullable=False)
    full_address = Column(Text, nullable=False)
    comment = Column(Text, nullable=False)
    telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
    ticketID = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    geometry = Column(Geography(geometry_type="POINT", srid=4326, dimension=2))
    tags: Mapped[list[Tag_Assistance]] = relationship(
        argument=Tag_Assistance, secondary=assistance_tag_connection, lazy="subquery"
    )
    sender = relationship(User, lazy="subquery")


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


class Staff(Base, UserMixin):
    """Модель персонала"""

    first_name = Column(String(255))
    last_name = Column(String(255))
    login = Column(String(255), unique=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    active = Column(Boolean())
    roles = relationship("Role", secondary=roles_users, backref=backref("users", lazy="dynamic"))

    def has_role(self, *args):
        return set(args).issubset({role.name for role in self.roles})

    def get_id(self):
        return self.id

    def __unicode__(self):
        return self.login

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
