from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.core.db.repository.user_repository import crud_user


async def check_user_in_db(
    telegram_id,
    session: AsyncSession
) -> bool:
    user_id = await crud_user.get_user_id_by_telegram_id(telegram_id, session)
    if user_id is not None:
        return True
    else:
        return False


class UserCreate(BaseModel):
    telegram_id = int
    is_banned = Optional[bool]

    class Config:
        arbitrary_types_allowed = True


async def create_new_user(
    telegram_id: UserCreate,
    session: AsyncSession
):
    if await check_user_in_db(telegram_id, session) is False:
        new_user = await crud_user.create_user(telegram_id, session)
        return new_user
