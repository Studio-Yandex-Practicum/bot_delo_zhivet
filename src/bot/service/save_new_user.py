from typing import Optional

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.repository.user_repository import crud_user


async def check_user_in_db(telegram_id, session: AsyncSession) -> bool:
    user = await crud_user.get_user_by_telegram_id(telegram_id, session)
    return user


class UserCreate(BaseModel):
    telegram_id = int
    telegram_username = str
    is_banned = Optional[bool]

    class Config:
        arbitrary_types_allowed = True


async def create_new_user(user_data: UserCreate, session: AsyncSession):
    new_user = await crud_user.create(user_data, session)
    return new_user
