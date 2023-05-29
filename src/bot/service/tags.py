from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_async_session
from src.core.db.model import Tag_Assistance, Tag_Pollution
from src.core.db.repository.tags_repository import (
    crud_tag_assistance, crud_tag_pollution,
)


async def get_all_assistance_tags(session: AsyncSession = None) -> list[Tag_Assistance]:
    """Получить все теги соц. помощи, отсортированные по name"""
    if session is None:
        session_generator = get_async_session()
        session = await session_generator.asend(None)
    tags = await crud_tag_assistance.get_all_sorted_by_attribute("name", session)
    return tags


async def get_all_pollution_tags(session: AsyncSession = None) -> list[Tag_Pollution]:
    """Получить все теги загрязнения, отсортированные по name"""
    if session is None:
        session_generator = get_async_session()
        session = await session_generator.asend(None)
    tags = await crud_tag_pollution.get_all_sorted_by_attribute("name", session)
    return tags


async def check_pollution_tag_exists(tag_id, session: AsyncSession = None) -> bool:
    if session is None:
        session_generator = get_async_session()
        session = await session_generator.asend(None)
    tag = await crud_tag_pollution.get(tag_id, session)
    if tag:
        return True
    False


async def check_social_tag_exists(tag_id, session: AsyncSession = None) -> bool:
    if session is None:
        session_generator = get_async_session()
        session = await session_generator.asend(None)
    tag = await crud_tag_assistance.get(tag_id, session)
    if tag:
        return True
    False
