from typing import Optional
from dadata import Dadata
from pydantic import BaseModel
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_async_session
from src.core.db.repository.assistance_disabled_repository import crud_assistance_disabled
from bot.handlers.state_constants import (
    SOCIAL_COMMENT,
    SOCIAL_ADDRESS,
    TELEGRAM_ID
)


token = '678a0ddcf1c81baff82a28bc613932cf1dcefdbd'
secret = "8ad83c107768fa78c0e280c273ed22ad91cfca31"
dadata = Dadata(token, secret)


def get_fields_from_data(data):
    result = dadata.clean('address', data[SOCIAL_ADDRESS])
    if result['city'] is None:
        city = result['settlement']
    else:
        city = result['city']
    street = result['street_with_type']
    house = result['house']
    latitude = result['geo_lat']
    longitude = result['geo_lon']
    comment = data[SOCIAL_COMMENT]
    telegram_id = data[TELEGRAM_ID]
    # ticketID = data.ticketID
    return dict(
        city = city,
        street = street,
        house = house,
        comment = comment,
        telegram_id = telegram_id,
        # ticketID = ticketID,
        latitude = latitude,
        longitude = longitude
    )


class SocialProblemCreate(BaseModel):
    city = str
    street = str
    house = int
    # comment = Optional[str]
    # telegram_id = Optional[int]
    # # ticketID = Optional[int]
    # latitude = Optional[float]
    # longitude = Optional[float]

    class Config:
        arbitrary_types_allowed = True


async def create_new_social(
        data: SocialProblemCreate,
        session: AsyncSession = Depends(get_async_session),
):
    data_in_dict = get_fields_from_data(data)
    # social_problem = SocialProblemCreate(**data_in_dict)
    new_social_problem = await crud_assistance_disabled.create(data_in_dict, session)
    return new_social_problem
