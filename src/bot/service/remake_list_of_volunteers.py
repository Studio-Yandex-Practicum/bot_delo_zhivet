from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.tracker import client
from src.core.db.model import Assistance_disabled, Pollution
from src.core.db.repository.volunteer_repository import crud_volunteer
from src.bot.service.get_issues_with_statuses import (
    get_issues_with_statuses, issues_updater
)
from src.bot.service.volunteer import volunteers_description


async def reshape_issues_description(
    session: AsyncSession
) -> None:
    '''
    Одноразовый скрипт для изменения описания доступных волонтеров
    в открытых задачах
    '''
    objects = []
    issues = []
    _, issues_keys = get_issues_with_statuses()
    for model in Assistance_disabled, Pollution:
        stmt = select(model).where(model.ticketID in issues_keys)
        issues = await session.execute(stmt)
        objects.extend(issues.scalars().all())
    for obj in objects:
        issue = client.issues[obj.ticketID]
        if "\n\nВолонтёров поблизости не нашлось" in issue.description:
            desc, _ = issue.description.split(
                "\n\nВолонтёров поблизости не нашлось"
            )
        else:
            desc, _ = issue.description.split(
                '\n\nВолонтёры поблизости'
            )
        volunteers = crud_volunteer.get_volunteers_by_point(
            obj.longitude, obj.latitude, session
        )
        desc += volunteers_description(volunteers)
        issue.description = desc
        issues.append(issue)
    issues_updater(issues)
