from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


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
        return db_obj.scalars().first()

    async def get_multi(self, session: AsyncSession):
        """get all records from DB."""
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in,
        session: AsyncSession,
    ):
        """create new record."""
        # ! уточнить формат входных данных для записи словарь или объект модели
        # obj_in_data = obj_in.dict()
        # db_obj = self.model(**obj_in_data)
        db_obj = obj_in
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession,
    ):
        """Update record."""
        db_obj_keys = [column.key for column in db_obj.__table__.columns]
        update_obj = obj_in.__dict__
        update_obj.pop("_sa_instance_state", None)
        obj_in_keys = update_obj.keys()
        for db_key in db_obj_keys:
            if db_key != "id" and db_key in obj_in_keys:
                db_value = getattr(db_obj, db_key)
                update_value = getattr(obj_in, db_key)
                if update_value != db_value:
                    setattr(db_obj, db_key, update_value)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

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
        return db_obj.scalars().first()
