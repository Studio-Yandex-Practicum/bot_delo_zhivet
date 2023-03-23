from typing import Optional

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.repository.assistance_disabled_repository import crud_assistance_disabled


class SocialProblemCreate(BaseModel):
    city = str
    street = str
    house = int
    comment = Optional[str]
    telegram_id = Optional[int]
    ticketID = Optional[int]
    latitude = float
    longitude = float
    geometry = str

    class Config:
        arbitrary_types_allowed = True


async def create_new_social(
    data: SocialProblemCreate,
    session: AsyncSession,
):
    new_social_problem = await crud_assistance_disabled.create(data, session)
    return new_social_problem
