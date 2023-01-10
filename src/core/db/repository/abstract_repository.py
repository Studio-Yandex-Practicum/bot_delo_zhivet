from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.loggers import get_logger

logger = get_logger()


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

        logger.info("Получена запись из БД.")

        return db_obj.scalars().first()

    async def get_multi(self, session: AsyncSession):
        """get all records from DB."""
        db_objs = await session.execute(select(self.model))

        logger.info("Получены все записи из БД.")

        return db_objs.scalars().all()

    async def create(
        self,
        obj_in,
        session: AsyncSession,
    ):
        """create new record."""
        # ! уточнить формат фходных данных для записи словарь или объект модели
        # obj_in_data = obj_in.dict()
        # db_obj = self.model(**obj_in_data)
        db_obj = obj_in
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)

        logger.info("Создана запись в БД.")

        return db_obj

    # async def update(
    #     self,
    #     db_obj,
    #     obj_in,
    #     session: AsyncSession,
    # ):
    #     """Update record."""
    #     # obj_data = jsonable_encoder(db_obj)
    #     # update_data = obj_in.dict(exclude_unset=True)
    #     # obj_data = db_obj.__mapper__
    #     # print(obj_data)
    #     # update_data = obj_in.__dict__.pop("_sa_instance_state", None)
    #     # update_data = obj_in.__dict__
    #     for field in obj_data:
    #         if field in update_data:
    #             setattr(db_obj, field, update_data[field])
    #     session.add(db_obj)
    #     await session.commit()
    #     await session.refresh(db_obj)
    #     return db_obj

    async def remove(
        self,
        db_obj,
        session: AsyncSession,
    ):
        """Remove record"""
        await session.delete(db_obj)
        await session.commit()
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

        logger.info("Удалена запись из БД.")

        return db_obj.scalars().first()
