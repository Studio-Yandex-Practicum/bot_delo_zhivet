from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from core.config import settings
from src.core.db.model import AbstractTag, Tag_Assistance, Tag_Pollution
from src.core.db.repository.abstract_repository import CRUDBase

logger = get_logger(settings.logger_name)


class TagCRUD(CRUDBase):
    async def get_all_sorted_by_attribute(self, attrs_name_list: list[str], session: AsyncSession) -> list[AbstractTag]:
        """Получить все теги отсортированные по заданому атрибуту."""
        statement = select(self.model)
        for attr_name in attrs_name_list:
            attr = getattr(self.model, attr_name)
            statement = statement.order_by(asc(attr))
        db_objs = await session.execute(statement)
        logger.info(f"Retrieved all records from database: {self.model.__name__}.")
        return db_objs.scalars().all()

    async def get_tags_list_from_tag_id_list(self, tag_id_list: list[str], session: AsyncSession) -> list[AbstractTag]:
        """
        Находит в базе теги по id из списка и возвращает список тегов.
        Не выдает ошибок если таких тегов нет в базе.
        """
        db_tags = []
        for tag_id in tag_id_list:
            db_tag = await self.get(tag_id, session)
            if db_tag is not None:
                db_tags.append(db_tag)
        return db_tags

    async def get_some_tag(self, session: AsyncSession) -> AbstractTag:
        """Достает из базы какой-то тег Удобно для проверки что теги вообще есть."""
        db_tag = await session.execute(select(self.model))
        db_tag = db_tag.scalars().first()
        logger.info(f"Retrieved record from database: {db_tag}.")
        return db_tag


crud_tag_assistance = TagCRUD(Tag_Assistance)
crud_tag_pollution = TagCRUD(Tag_Pollution)
