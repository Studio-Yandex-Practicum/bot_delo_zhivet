from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from core.config import settings
from src.core.db.model import Tag_Assistance, Tag_Pollution
from src.core.db.repository.abstract_repository import CRUDBase

logger = get_logger(settings.logger_name)


class TagCRUD(CRUDBase):
    async def get_all_sorted_by_attribute(self, attr_name: str, session: AsyncSession):
        attr = getattr(self.model, attr_name)
        statement = select(self.model).order_by(attr)
        db_objs = await session.execute(statement)
        logger.info(f"Retrieved all records from database: {self.model.__name__}.")
        return db_objs.scalars().all()


crud_tag_assistance = TagCRUD(Tag_Assistance)
crud_tag_pollution = TagCRUD(Tag_Pollution)
