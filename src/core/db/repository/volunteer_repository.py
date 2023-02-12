from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db.model import Volunteer
from src.core.db.repository.abstract_repository import CRUDBase


class VolunteerCRUD(CRUDBase):
    async def get_volunteers_by_point(
        self,
        lat: float,
        lon: float,
        session: AsyncSession,
    ):
        stmt = select(
            Volunteer.telegram_username, Volunteer.has_car, Volunteer.city, Volunteer.ticketID
        ).where(
            func.ST_DWithin(Volunteer.geom,
                            func.ST_GeomFromText(f'SRID=4326;POINT({lat} {lon})'),
                            Volunteer.radius, use_spheroid=False)
        ).order_by(desc(Volunteer.created_at))
        volunteers = await session.execute(stmt)
        return volunteers
    

crud_volunteer = VolunteerCRUD(Volunteer)
