from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from core.config import settings

logger = get_logger(settings.logger_name)


class CRUDBase:
    """Базовый класс CRUD операций."""

    def __init__(self, model):
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ):
        """get one record by id from DB."""
        db_obj = await session.execute(select(self.model).where(self.model.id == obj_id))
        db_obj = db_obj.scalars().first()
        logger.info(f"Retrieved record from database: {db_obj}.")
        return db_obj

    async def get_multi(self, session: AsyncSession):
        """get all records from DB."""
        db_objs = await session.execute(select(self.model))
        logger.info(f"Retrieved all records from database: {self.model.__name__}.")
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in,
        session: AsyncSession,
    ):
        """create new record."""
        db_obj = self.model(**obj_in)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        logger.info(f"Database record created: {db_obj}.")
        return db_obj

    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession,
    ):
        """Update record."""
        db_obj_keys = [column.key for column in db_obj.__table__.columns]
        update_obj = obj_in
        obj_in_keys = update_obj.keys()
        for db_key in db_obj_keys:
            if db_key != "id" and db_key in obj_in_keys:
                db_value = getattr(db_obj, db_key)
                update_value = obj_in[db_key]
                if update_value != db_value:
                    setattr(db_obj, db_key, update_value)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        logger.info(f"Database record updated: {db_obj}.")
        return db_obj

    async def remove(
        self,
        db_obj,
        session: AsyncSession,
    ):
        """Remove record"""
        await session.delete(db_obj)
        await session.commit()
        logger.info(f"Database record deleted: {db_obj}.")
        return db_obj

    async def get_by_attribute(
        self,
        attr_name: str,
        attr_value: str,
        session: AsyncSession,
    ):
        """get record by attribute value from DB."""
        attr = getattr(self.model, attr_name)
        db_obj = await session.execute(select(self.model).where(attr == attr_value))
        db_obj = db_obj.scalars().first()
        logger.info("Retrieved record from database with " f"{attr_name} = {attr_value}: {db_obj}.")
        return db_obj

    async def get_exist_by_attribute(
        self,
        attr_name: str,
        attr_value: str,
        session: AsyncSession,
    ) -> bool:
        """get is record exists by attribute value from DB."""
        attr = getattr(self.model, attr_name)
        is_exists = await session.scalars(select(True).where(select(self.model).where(attr == attr_value).exists()))
        is_exists = is_exists.first()
        logger.info("Retrieved record exist from database with " f"{attr_name} = {attr_value}: {is_exists}.")
        return False if is_exists is None else True

    async def get_id_by_telegram_id(self, telegram_id: int, session: AsyncSession):
        db_id = await session.execute(select(self.model.id).where(self.model.telegram_id == telegram_id))
        id = db_id.scalars().all()[-1]
        return id
