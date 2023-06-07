from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.tracker import client
from src.bot.handlers.state_constants import POLLUTION, SOCIAL
from src.core.db.model import Volunteer
from src.core.db.repository.volunteer_repository import crud_volunteer


def get_issues_with_statuses(
    queues: list = [POLLUTION, SOCIAL],
    statuses: list = ['OPEN']
):
    issues = client.issues.find(
        filter=dict(queue=queues, status=statuses)
    )
    return issues


async def add_new_volunteer_to_issue(
    volunteer: Volunteer,
    session: AsyncSession
):
    FORMAT = "%d/%m/%Y"
    open_issues = get_issues_with_statuses()
    issues_in_radius = await crud_volunteer.get_issues_in_radius(
        volunteer, session
    )
    for issue in open_issues:
        if issue.key in issues_in_radius:
            description = issue.description
            description += (
                '\n\n' + date.today().strftime(FORMAT)
                + ' Найден новый волонтер '
            )
            description += 'с машиной' if volunteer.has_car else 'без машины'
            description += '\n' + (
                f'https://t.me/{volunteer.telegram_username}, {volunteer.ticketID}'
            )
            issue.update(description=description)
