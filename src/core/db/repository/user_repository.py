import backoff
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.loggers import get_logger
from src.core.backoff import JITTER, backoff_hdlr
from src.core.db.model import User
from src.core.db.repository.abstract_repository import CRUDBase

logger = get_logger()


class UserCRUD(CRUDBase):
    @backoff.on_exception(
        backoff.expo,
        exception=Exception,
        on_backoff=backoff_hdlr,
        max_tries=12,
        max_time=120,
        jitter=JITTER["RandomJitter_method"],
    )
    async def get_user_by_telegram_id(
        self,
        telegram_id: int,
        session: AsyncSession,
    ):
        user = await session.execute(select(User).where(User.telegram_id == telegram_id))
        return user.scalars().first()


crud_user = UserCRUD(User)
