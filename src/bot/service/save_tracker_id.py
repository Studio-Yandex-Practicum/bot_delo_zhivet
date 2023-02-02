import asyncio

from api.tracker import client
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.repository.assistance_disabled_repository import crud_assistance_disabled


async def save_tracker_id(
    summary,
    telegram_id,
    session: AsyncSession,
):
    await asyncio.sleep(3)
    issues = client.issues.find(filter={'summary': summary})
    key = [issue.key for issue in issues]
    _dict = {'ticketID': key[0]}
    db_id = await crud_assistance_disabled.get_id_by_telegram_id(telegram_id, session)
    db_obj = await crud_assistance_disabled.get(db_id, session)
    await crud_assistance_disabled.update(db_obj, _dict, session)
