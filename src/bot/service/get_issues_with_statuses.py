from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.tracker import client
from src.bot.handlers.state_constants import POLLUTION, SOCIAL
from src.core.db.model import Volunteer
from src.core.db.repository.volunteer_repository import crud_volunteer

FORMAT = "%d/%m/%Y"


def get_issues_with_statuses(queues: list = [POLLUTION, SOCIAL], statuses: list = ["OPEN"]):
    issues = client.issues.find(filter=dict(queue=queues, status=statuses))
    return issues


async def add_new_volunteer_to_issue(volunteer: Volunteer, session: AsyncSession):
    open_issues = get_issues_with_statuses()
    issues_in_radius = await crud_volunteer.get_issues_in_radius(volunteer, session)
    for issue in open_issues:
        if issue.key in issues_in_radius:
            description = issue.description
            description += "\n\n" + date.today().strftime(FORMAT) + " Найден новый волонтер "
            description += "с машиной" if volunteer.has_car else "без машины"
            description += "\n" + (f"https://t.me/{volunteer.telegram_username}, {volunteer.ticketID}")
            issue.update(description=description)


async def delete_volunteer_from_issue(volunteer: Volunteer, session: AsyncSession):
    open_issues = get_issues_with_statuses()
    issues_in_radius = await crud_volunteer.get_issues_in_radius(volunteer, session)
    for issue in open_issues:
        if issue.key in issues_in_radius:
            # Формируем новое описание без этого волонтера
            description = form_new_description(issue, volunteer)
            description += (
                f"\n\n{date.today().strftime(FORMAT)}:" " Эта задача больше не входит в радиус активности волонтера"
            )
            description += f"\n<{volunteer.telegram_username}, {volunteer.ticketID}>"
            issue.update(description=description)


def form_new_description(issue, volunteer):
    description = ""

    for vol in issue.volunteers:
        if vol.id != volunteer.id:
            description += f"...{vol.description}..."
