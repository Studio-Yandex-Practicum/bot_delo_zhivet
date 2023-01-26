from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, BigInteger, Float

from src.core.db.db import Base


class User(Base):
    """Model User."""
    telegram_id = Column(BigInteger, unique=True, nullable=False)


class Volunteer(Base):
    """Model Volunteer."""
    telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
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
    telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
    ticketID = Column(BigInteger, nullable=True)


class Assistance_disabled(Base):
    """Model Assistance_disabled. Инфо о помощи инвалиду."""

    city = Column(Text, nullable=False)
    street = Column(Text, nullable=False)
    house = Column(Text, nullable=False)
    comment = Column(Text, nullable=False)
    telegram_id = Column(BigInteger, ForeignKey("user.telegram_id"))
    ticketID = Column(Integer, nullable=True)
    latitude = Column(Integer, nullable=True)
    longitude = Column(Integer, nullable=True)



