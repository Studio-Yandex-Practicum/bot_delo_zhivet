from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.service.tags import check_social_tag_exists
from src.core.db.repository.assistance_disabled_repository import (
    crud_assistance_disabled,
)


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
    tag_id = Optional[UUID]

    class Config:
        arbitrary_types_allowed = True


async def create_new_social(
    data: SocialProblemCreate,
    session: AsyncSession,
):
    if "tag_id" in data:
        if not await check_social_tag_exists(data["tag_id"], session):
            data["tag_id"] = None
    new_social_problem = await crud_assistance_disabled.create(data, session)
    return new_social_problem
