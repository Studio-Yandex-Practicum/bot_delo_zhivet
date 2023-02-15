import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.tracker import client
from src.bot.handlers.state_constants import SLEEP_TIME
from src.core.db.repository.assistance_disabled_repository import crud_assistance_disabled
from src.core.db.repository.pollution_repository import crud_pollution
from src.core.db.repository.volunteer_repository import crud_volunteer


async def save_tracker_id_assistance_disabled(
    summary,
    telegram_id,
    session: AsyncSession,
):
    await asyncio.sleep(SLEEP_TIME)
    issues = client.issues.find(filter={"summary": summary})
    key = [issue.key for issue in issues]
    _dict = {"ticketID": key[0]}
    db_id = await crud_assistance_disabled.get_id_by_telegram_id(telegram_id, session)
    db_obj = await crud_assistance_disabled.get(db_id, session)
    await crud_assistance_disabled.update(db_obj, _dict, session)


async def save_tracker_id_volunteer(
    summary,
    telegram_id,
    session: AsyncSession,
):
    await asyncio.sleep(SLEEP_TIME)
    issues = client.issues.find(filter={"summary": summary})
    key = [issue.key for issue in issues]
    _dict = {"ticketID": key[0]}
    db_id = await crud_volunteer.get_id_by_telegram_id(telegram_id, session)
    db_obj = await crud_volunteer.get(db_id, session)
    await crud_volunteer.update(db_obj, _dict, session)


async def save_tracker_id_pollution(
    summary,
    telegram_id,
    file_path,
    session: AsyncSession,
):
    await asyncio.sleep(SLEEP_TIME)
    issues = client.issues.find(filter={"summary": summary})
    key = [issue.key for issue in issues]
    _dict = {"ticketID": key[0]}
    db_id = await crud_pollution.get_id_by_telegram_id(telegram_id, session)
    db_obj = await crud_pollution.get(db_id, session)
    await crud_pollution.update(db_obj, _dict, session)
    issue = client.issues[key[0]]
    issue.attachments.create(file_path)
