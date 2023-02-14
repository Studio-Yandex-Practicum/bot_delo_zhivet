import json

import backoff
import requests as requests
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.loggers import get_logger
from src.core.db.model import User
from src.core.db.repository.abstract_repository import CRUDBase

logger = get_logger()


def backoff_hdlr(details):
    # print("Backing off {wait:0.1f} seconds after {tries} tries ")
    logger.error("Error detected, %s attempt to connect to base", details.get("tries"))


# def save_dict_to_json(path, data):
#     logger.info('Saving new state file to %s', path)
#     with open(path, 'w') as fil:
#         fil.write(json.dumps(data))


class UserCRUD(CRUDBase):
    @backoff.on_exception(
        backoff.expo, on_backoff=backoff_hdlr, on_giveup=print("ALERT"), max_tries=10, max_time=20, exception=Exception
    )
    async def get_user_id_by_telegram_id(
        self,
        telegram_id: int,
        session: AsyncSession,
    ):
        user_id = await session.execute(select(User.id).where(User.telegram_id == telegram_id))
        return user_id.scalars().first()


crud_user = UserCRUD(User)
