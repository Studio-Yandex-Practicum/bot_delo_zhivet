from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, BigInteger, Float, \
    Boolean

from src.core.db.db import Base


class User(Base):
    """Модель пользователя"""

    telegram_id = Column(BigInteger, unique=True, nullable=False)
    is_banned = Column(Boolean, default=True)


class Volunteer(Base):
    """Модель волонтера"""

    telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
    name = Column(String(100), nullable=True)
    city = Column(String(100), nullable=False)
    phone = Column(String(13), unique=True, nullable=True)
    radius = Column(Integer, nullable=False)
    has_car = Column(Boolean, nullable=False)
    birthday = Column(Date, nullable=True)
    deleted_at = Column(DateTime(timezone=True))


class Pollution(Base):
    """Модель сообщения о загрязнении"""

    photo = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)
    telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
    ticketID = Column(BigInteger, nullable=True)


class Assistance_disabled(Base):
    """Модель сообщения о социальной помощи"""

    city = Column(Text, nullable=False)
    full_address = Column(Text, nullable=False)
    comment = Column(Text, nullable=False)
    telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
    ticketID = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
