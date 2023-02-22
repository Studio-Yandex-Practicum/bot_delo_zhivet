from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.model import Volunteer
from src.core.db.repository.volunteer_repository import crud_volunteer


class VolunteerCreate(BaseModel):
    telegram_id = int
    city = str
    full_address = str
    radius = int
    has_car = str
    latitude = float
    longitude = float
    geometry = str
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


async def create_volunteer(data: VolunteerCreate, session: AsyncSession):
    return await crud_volunteer.create(data, session)


async def update_volunteer(db_obj: Volunteer, data: VolunteerCreate, session: AsyncSession):
    return await crud_volunteer.update(db_obj, data, session)


def volunteers_description(volunteers):
    description = ""
    description_add_hascar = ""
    description_add_nocar = ""
    volunteer_counter = 0
    for volunteer in volunteers:
        volunteer_counter += 1
        volunteer_description = (
            f"https://t.me/{volunteer.telegram_username}, {volunteer.city}\n{volunteer.ticketID}\n\n"
        )
        if volunteer.has_car:
            description_add_hascar += volunteer_description
        else:
            description_add_nocar += volunteer_description

    if not volunteer_counter:
        description += "\n---- \n\nВолонтёров поблизости не нашлось"
    else:
        description += "\n---- \n\nВолонтёры поблизости\n\n"
        if description_add_hascar:
            description += "* с авто:\n\n" + description_add_hascar
        if description_add_nocar:
            description += "* без авто:\n\n" + description_add_nocar
    return description
