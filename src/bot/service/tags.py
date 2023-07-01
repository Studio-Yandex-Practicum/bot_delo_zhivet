from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.model import AbstractTag, Tag_Assistance, Tag_Pollution
from src.core.db.repository.tags_repository import crud_tag_assistance, crud_tag_pollution


async def get_all_assistance_tags(session: AsyncSession) -> list[Tag_Assistance]:
    """Получить все теги соц. помощи, отсортированные по name"""
    tags = await crud_tag_assistance.get_all_sorted_by_attribute(["name"], session)
    return tags


async def get_all_pollution_tags(session: AsyncSession) -> list[Tag_Pollution]:
    """Получить все теги загрязнения, отсортированные по name"""
    tags = await crud_tag_pollution.get_all_sorted_by_attribute(["name"], session)
    return tags


def get_chosen_tags_names(all_tags_list: list[AbstractTag], chosen_tags_ids_list: list) -> list[str]:
    names = []
    for tag in all_tags_list:
        if str(tag.id) in chosen_tags_ids_list:
            names.append(str(tag.name))
    return names


async def check_pollution_tags_are_in_db(session: AsyncSession) -> bool:
    tag = await crud_tag_pollution.get_some_tag(session)
    return tag


async def check_assistance_tags_are_in_db(session: AsyncSession) -> bool:
    tag = await crud_tag_assistance.get_some_tag(session)
    return tag
