from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.model import Assistance_disabled
from src.core.db.repository.abstract_repository import CRUDBase


class AssistanceCRUD(CRUDBase):

    async def get_full_address_by_telegram_id(
        self,
        telegram_id: int,
        session: AsyncSession
    ):
        full_address = await session.execute(
            select(Assistance_disabled.full_address).where(
                Assistance_disabled.telegram_id == telegram_id
            )
        )
        full_address = full_address.scalars().all()[-1]
        return full_address


crud_assistance_disabled = AssistanceCRUD(Assistance_disabled)
