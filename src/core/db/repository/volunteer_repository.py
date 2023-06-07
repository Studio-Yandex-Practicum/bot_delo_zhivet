from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.model import Pollution, Assistance_disabled, Volunteer
from src.core.db.repository.abstract_repository import CRUDBase


class VolunteerCRUD(CRUDBase):
    async def get_volunteer_by_telegram_id(
        self,
        telegram_id: int,
        session: AsyncSession,
    ) -> Volunteer:
        user_id = await session.execute(select(Volunteer).where(Volunteer.telegram_id == telegram_id))
        return user_id.scalars().first()

    async def get_volunteers_by_point(
        self,
        longitude: float,
        latitude: float,
        session: AsyncSession,
    ):
        stmt = (
            select(Volunteer.telegram_username, Volunteer.has_car, Volunteer.city, Volunteer.ticketID)
            .where(
                and_(
                    Volunteer.is_banned.is_(False),
                    func.ST_DWithin(
                        Volunteer.geometry,
                        func.ST_GeomFromText(f"SRID=4326;POINT({longitude} {latitude})"),
                        Volunteer.radius,
                        use_spheroid=False,
                    ),
                )
            )
            .order_by(Volunteer.radius, desc(Volunteer.created_at))
        )
        volunteers = await session.execute(stmt)
        return volunteers.all()

    async def get_issues_in_radius(
        self,
        volunteer: Volunteer,
        session: AsyncSession,
        models: list = [Assistance_disabled, Pollution]
    ) -> list:
        result = []
        for model in models:
            stmt = select(model.ticketID).where(
                func.ST_DWITHIN(
                    model.geometry,
                    func.ST_GeomFromText(
                        f'SRID=4326;POINT({volunteer.longitude} {volunteer.latitude})'
                    ),
                    volunteer.radius,
                    use_spheroid=False
                )
            )
            issues = await session.execute(stmt)
            result.extend(issues.scalars().all())
        return result


crud_volunteer = VolunteerCRUD(Volunteer)
