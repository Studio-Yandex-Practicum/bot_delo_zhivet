import os
from datetime import datetime
from typing import Optional

from dadata import Dadata
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.repository.volunteer_repository import crud_volunteer

token = os.environ['DADATA_TOKEN']
secret = os.environ['DADATA_SECRET']
dadata = Dadata(token, secret)


class VolunteerCreate(BaseModel):
    telegram_id = int
    city = str
    full_address = str
    radius = int
    has_car = str
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


async def create_new_volunteer(
        data: VolunteerCreate,
        session: AsyncSession,
):
    new_volunteer = await crud_volunteer.create(data, session)
    return new_volunteer
