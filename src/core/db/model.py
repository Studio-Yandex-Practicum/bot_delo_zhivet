import enum

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON

from src.core.db.db import Base


class StatusUser(enum.Enum):
    """Status chinces for model User."""

    pending = 1
    verified = 2
    declined = 3


class StatusMember(enum.Enum):
    """Status chinces for model Member."""

    active = 1
    excluded = 2


class StatusRequest(enum.Enum):
    """Status chinces for model Request."""

    pending = 1
    approved = 2
    declined = 3


class StatusShift(enum.Enum):
    """Status chinces for model Shift."""

    preparing = 1
    started = 2
    finished = 3
    cancelled = 4


class StatusReport(enum.Enum):
    """Status chinces for model Report."""

    waiting = 1
    reviewing = 2
    approved = 3
    declined = 4


class StatusUserTask(enum.Enum):
    """Status chinces for model Report."""

    new = 1
    wait_report = 2
    under_review = 3
    approved = 4
    declined = 5


class User(Base):
    """Model User."""

    name = Column(String(100), index=True, nullable=False)
    surname = Column(String(100), index=True, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    city = Column(String(100), index=True, nullable=False)
    phone_number = Column(String(13), unique=True, index=True, nullable=False)
    telegram_id = Column(String(64), unique=True, index=True, nullable=False)
    volunteer_id = Column(Integer, ForeignKey("volunteer.id"), nullable=True)
    status = Column(Enum(StatusUser), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


class Member(Base):
    """Model Member."""

    user_id = Column(Integer, ForeignKey("user.id"))
    shift_id = Column(Integer, ForeignKey("shift.id"))
    numbers_lombaryers = Column(Integer, default=0)
    status = Column(Enum(StatusMember), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


class Request(Base):
    """Model Reqiest."""

    user_id = Column(Integer, ForeignKey("user.id"))
    shift_id = Column(Integer, ForeignKey("shift.id"))
    attempt_number = Column(Integer, default=0)
    status = Column(Enum(StatusMember), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


class Shift(Base):
    """Model Shift."""

    sequence_number = Column(Integer, default=0)
    title = Column(String(50), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    final_message = Column(String(255), index=True, nullable=False)
    tasks = Column(JSON)
    status = Column(Enum(StatusShift), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


class Report(Base):
    """Model Report."""

    member_id = Column(Integer, ForeignKey("member.id"))
    shift_id = Column(Integer, ForeignKey("shift.id"))
    task_id = Column(Integer, ForeignKey("task.id"))
    task_date = Column(DateTime(timezone=True), nullable=True)
    report_url = Column(String(255), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), nullable=True)
    attempt_number = Column(Integer, default=0)
    status = Column(Enum(StatusReport), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


class Task(Base):
    """Model Task."""

    description = Column(Text, nullable=False)
    ulr = Column(String(255), nullable=False)
    status = Column(Enum(StatusUserTask), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


class Volunteer(Base):
    city = Column(String(100), nullable=False)
    radius = Column(Text, nullable=False)
    car = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))
