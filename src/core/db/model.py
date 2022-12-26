import enum

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
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


class StatusReport(enum.Enum):
    """Status chinces for model Report."""

    waiting = 1
    reviewing = 2
    approved = 3
    declined = 4


class User(Base):
    """Model User."""

    name = Column(String(100), index=True, nullable=False)
    surname = Column(String(100), index=True, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    city = Column(String(100), index=True, nullable=False)
    phone_number = Column(String(13), unique=True, index=True, nullable=False)
    telegram_id = Column(String(64), unique=True, index=True, nullable=False)
    status = Column(Enum(StatusUser), nullable=False, default=StatusUser.pending)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Member(Base):
    """Model Member."""

    user_id = Column(Integer, ForeignKey("user.id"))
    shift_id = Column(Integer, ForeignKey("shift.id"))
    numbers_lombaryers = Column(Integer, default=0)
    status = Column(Enum(StatusMember), nullable=False, default=StatusMember.active)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Request(Base):
    """Model Reqiest."""

    user_id = Column(Integer, ForeignKey("user.id"))
    shift_id = Column(Integer, ForeignKey("shift.id"))
    attempt_number = Column(Integer, default=0)
    status = Column(Enum(StatusMember), nullable=False, default=StatusMember.active)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Shift(Base):
    """Model Shift."""

    sequence_number = Column(Integer, default=0)
    title = Column(String(50), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    final_message = Column(String(255), index=True, nullable=False)
    tasks = Column(JSON)
    status = Column(Enum(StatusShift), nullable=False, default=StatusShift.preparing)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Report(Base):
    """Model Report."""

    member_id = Column(Integer, ForeignKey("member.id"))
    shift_id = Column(Integer, ForeignKey("shift.id"))
    task_id = Column(Integer, ForeignKey("task.id"))
    task_date = Column(DateTime(timezone=True), nullable=True)
    report_url = Column(String(255), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), nullable=True)
    attempt_number = Column(Integer, default=0)
    status = Column(Enum(StatusReport), nullable=False, default=StatusReport.reviewing)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Task(Base):
    """Model Task."""

    description = Column(Text, nullable=False)
    ulr = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
