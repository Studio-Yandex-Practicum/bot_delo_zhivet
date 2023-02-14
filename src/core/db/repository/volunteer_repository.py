from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.model import Volunteer
from src.core.db.repository.abstract_repository import CRUDBase


class VolunteerCRUD(CRUDBase):
    async def get_volunteer_by_telegram_id(
        self,
        telegram_id: int,
        session: AsyncSession,
    ):
        user_id = await session.execute(select(Volunteer).where(Volunteer.telegram_id == telegram_id))
        return user_id.scalars().first()


crud_volunteer = VolunteerCRUD(Volunteer)
