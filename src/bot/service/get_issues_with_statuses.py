from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.tracker import client
from src.bot.handlers.state_constants import POLLUTION, SOCIAL
from src.core.db.model import Volunteer
from src.core.db.repository.volunteer_repository import crud_volunteer


NEW_VOLUNTEER_DATE_FORMAT = "%d/%m/%Y"


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
) -> None:
    open_issues = get_issues_with_statuses()
    issues_in_radius = await crud_volunteer.get_issues_in_radius(
        volunteer, session
    )
    telegram_link = f'https://t.me/{volunteer.telegram_username}'
    for issue in open_issues:
        if issue.key in issues_in_radius:
            updated_issue_description = []
            for description in issue.description.split('\n\n'):
                if description == 'Волонтёров поблизости не нашлось':
                    updated_issue_description.append('Волонтёры поблизости')
                elif telegram_link not in description:
                    updated_issue_description.append(description)
            updated_issue_description.append(
                date.today().strftime(NEW_VOLUNTEER_DATE_FORMAT) + ' Найден новый волонтер'
                + f'\nhttps://t.me/{volunteer.telegram_username}, {volunteer.ticketID}'
            )
            issue.update(description='\n\n'.join(updated_issue_description))
