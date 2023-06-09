from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.handlers.state_constants import (
    CITY, COMMENT, GEOM, LATITUDE, LONGITUDE, NO_COMMENT_PHASE, SOCIAL,
    SOCIAL_COMMENT, SOCIAL_TAGS, TAGS, TELEGRAM_ID,
)
from src.core.db.model import Assistance_disabled
from src.core.db.repository.assistance_disabled_repository import (
    crud_assistance_disabled,
)
from src.core.db.repository.tags_repository import crud_tag_assistance


class SocialProblemCreate(BaseModel):
    city = str
    full_address: str
    comment = Optional[str]
    telegram_id = Optional[int]
    latitude = float
    longitude = float
    geometry = str
    tags = Optional[list[UUID]]

    class Config:
        arbitrary_types_allowed = True


async def create_new_social(
    data: SocialProblemCreate,
    session: AsyncSession,
):
    new_social_problem = await crud_assistance_disabled.create(data, session)
    return new_social_problem


async def create_new_social_dict_from_data(user_id: int, data: dict, session) -> dict:
    """Перекладывает данные из data в словарь который подходит для создания Assistance_disabled"""
    mandatory_fields = [LATITUDE, LONGITUDE, CITY, "full_address"]
    new_social_dict: dict = {TELEGRAM_ID: user_id}
    new_social_dict[GEOM] = f"POINT({data[LONGITUDE]} {data[LATITUDE]})"
    for field in mandatory_fields:
        new_social_dict[field] = data[field]
    if SOCIAL_COMMENT in data:
        new_social_dict[COMMENT] = data[SOCIAL_COMMENT]

    if SOCIAL_TAGS in data:
        new_social_dict[TAGS] = await crud_tag_assistance.get_tags_list_from_tag_id_list(data[SOCIAL_TAGS], session)
    return new_social_dict


def create_new_social_message_for_tracker(social: Assistance_disabled, volunteers_description: str) -> dict:
    """Создает словарь сообщения для отправки в треккер"""
    comment = social.comment if social.comment else NO_COMMENT_PHASE
    description = f"""
    Ник в телеграмме оставившего заявку: {social.sender.telegram_username}
    Комментарий к заявке: {comment}
    """
    description += volunteers_description
    return {
        "queue": SOCIAL,
        "summary": social.full_address,
        "description": description,
        "tags": [str(tag) for tag in social.tags],
    }
