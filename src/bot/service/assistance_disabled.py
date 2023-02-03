import os
from typing import Optional

from dadata import Dadata
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.state_constants import (SOCIAL_ADDRESS, SOCIAL_COMMENT,
                                          TELEGRAM_ID)
from src.core.db.repository.assistance_disabled_repository import \
    crud_assistance_disabled

token = os.environ['DADATA_TOKEN']
secret = os.environ['DADATA_SECRET']
dadata = Dadata(token, secret)


def get_fields_from_data(data):
    result = dadata.suggest('address', data[SOCIAL_ADDRESS])[0]
    if result['data']['settlement_with_type'] is not None:
        city = result['data']['settlement_with_type']
    else:
        city = result['data']['city_with_type']
    full_address = result['unrestricted_value']
    latitude = float(result['data']['geo_lat'])
    longitude = float(result['data']['geo_lon'])
    comment = data[SOCIAL_COMMENT]
    telegram_id = data[TELEGRAM_ID]
    return dict(
        city=city,
        full_address=full_address,
        comment=comment,
        telegram_id=telegram_id,
        latitude=latitude,
        longitude=longitude,
    )


class SocialProblemCreate(BaseModel):
    city = str
    street = str
    house = int
    comment = Optional[str]
    telegram_id = Optional[int]
    ticketID = Optional[int]
    latitude = Optional[float]
    longitude = Optional[float]

    class Config:
        arbitrary_types_allowed = True


async def create_new_social(
        data: SocialProblemCreate,
        session: AsyncSession,
):
    data_in_dict = get_fields_from_data(data)
    new_social_problem = await crud_assistance_disabled.create(data_in_dict, session)
    return new_social_problem
