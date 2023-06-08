"""Импорты класса Base и всех моделей для Alembic."""
from src.core.db.db import Base  # noqa
from src.core.db.model import (  # noqa
    Assistance_disabled, Pollution, Tag_Assistance, Tag_Pollution, User,
    Volunteer,
)
