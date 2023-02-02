import os
from datetime import datetime
from typing import Optional

from dadata import Dadata
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.state_constants import (FIRST_NAME, LAST_NAME,
                                          SPECIFY_ACTIVITY_RADIUS,
                                          SPECIFY_CAR_AVAILABILITY,
                                          SPECIFY_CITY, TELEGRAM_ID,
                                          TELEGRAM_USERNAME)
from src.core.db.repository.volunteer_repository import crud_volunteer

token = os.environ['DADATA_TOKEN']
secret = os.environ['DADATA_SECRET']
dadata = Dadata(token, secret)


def get_fields_from_data_volunteer(data):
    result = dadata.suggest('address', data[SPECIFY_CITY])[0]
    if result['data']['settlement_with_type'] is not None:
        city = result['data']['settlement_with_type']
    else:
        city = result['data']['city_with_type']
    full_address = result['unrestricted_value']
    latitude = float(result['data']['geo_lat'])
    longitude = float(result['data']['geo_lon'])
    telegram_id = data[TELEGRAM_ID]
    telegram_username = data[TELEGRAM_USERNAME]
    first_name = data[FIRST_NAME]
    last_name = data[LAST_NAME]
    radius = data[SPECIFY_ACTIVITY_RADIUS]
    if data[SPECIFY_CAR_AVAILABILITY] == 'Yes':
        has_car = True
    else:
        has_car = False

    return dict(
        city=city,
        full_address=full_address,
        telegram_id=telegram_id,
        latitude=latitude,
        longitude=longitude,
        telegram_username=telegram_username,
        first_name=first_name,
        last_name=last_name,
        radius=radius,
        has_car=has_car
    )


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
    data_in_dict = get_fields_from_data_volunteer(data)
    new_volunteer = await crud_volunteer.create(data_in_dict, session)
    return new_volunteer
