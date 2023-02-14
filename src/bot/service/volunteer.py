from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.handlers.state_constants import TELEGRAM_ID
from src.core.db.repository.volunteer_repository import crud_volunteer


class VolunteerCreate(BaseModel):
    telegram_id = int
    city = Optional[str]
    full_address = Optional[str]
    radius = Optional[int]
    has_car = Optional[str]
    latitude = Optional[float]
    longitude = Optional[float]
    telegram_username = Optional[str]
    first_name = Optional[str]
    last_name = Optional[str]
    phone = Optional[str]
    birthday = Optional[datetime.date]
    is_banned = Optional[bool]
    ticketID = Optional[str]

    class Config:
        arbitrary_types_allowed = True


async def check_volunteer_in_db(telegram_id, session: AsyncSession):
    volunteer = await crud_volunteer.get_volunteer_by_telegram_id(telegram_id, session)
    if not volunteer:
        return None
    return volunteer


async def create_update_volunteer(
    data: VolunteerCreate,
    session: AsyncSession,
):
    db_obj = await check_volunteer_in_db(data[TELEGRAM_ID], session)
    if db_obj is None:
        await crud_volunteer.create(obj_in=data, session=session)
        return None
    else:
        await crud_volunteer.update(db_obj, data, session)
        return db_obj.ticketID
