"""Импорты класса Base и всех моделей для Alembic."""
from src.core.db.db import Base  # noqa
from src.core.db.model import (  # noqa
    Assistance_disabled,
    Member,
    Pollution,
    Report,
    Request,
    Shift,
    Task,
    User,
    Volunteer,
)
