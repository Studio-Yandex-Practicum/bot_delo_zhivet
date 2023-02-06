from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.model import User
from src.core.db.repository.abstract_repository import CRUDBase
from bot.handlers.state_constants import TELEGRAM_ID
from bot.handlers.loggers import get_logger

logger = get_logger()


class UserCRUD(CRUDBase):

    async def get_user_id_by_telegram_id(
        self,
        telegram_id: int,
        session: AsyncSession,
    ):
        user_id = await session.execute(
            select(User.id).where(
                User.telegram_id == telegram_id
            )
        )
        return user_id.scalars().first()

    async def create_user(
        self,
        telegram_id: int,
        session: AsyncSession
    ):
        telegram_id_dict = {
            TELEGRAM_ID: telegram_id
        }
        db_obj = self.model(**telegram_id_dict)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        logger.info(f"Database record created: {db_obj}.")
        return db_obj


crud_user = UserCRUD(User)
