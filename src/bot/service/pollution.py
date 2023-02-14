from typing import Optional

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.repository.pollution_repository import crud_pollution


class PollutionCreate(BaseModel):
    photo = str
    latitude = float
    longitude = float
    geometry = str
    comment = Optional[str]
    telegram_id = int
    ticketID = Optional[str]

    class Config:
        arbitrary_types_allowed = True


async def create_new_pollution(
    data: PollutionCreate,
    session: AsyncSession,
):
    new_social_problem = await crud_pollution.create(data, session)
    return new_social_problem
