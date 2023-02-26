from sqlalchemy.ext.asyncio import AsyncSession


async def save_tracker_id(
    crud_model,
    tracker_id,
    telegram_id,
    session: AsyncSession,
):
    _dict = {"ticketID": tracker_id}
    db_id = await crud_model.get_id_by_telegram_id(telegram_id, session)
    db_obj = await crud_model.get(db_id, session)
    await crud_model.update(db_obj, _dict, session)
