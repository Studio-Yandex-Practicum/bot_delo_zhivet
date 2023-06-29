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
            # Уведомляем, что волонтер больше не поможет
            notify_volunteer_deleted(issue, volunteer)


def notify_volunteer_deleted(issue, volunteer):
    comment_text = f"{volunteer.telegram_username} больше не может помочь..."
    if comment_text not in [c.text for c in issue.comments]:
        add_comment(issue, comment_text)


def add_comment(issue, text):
    issue.comments.create(text=text)


def form_new_description(issue, volunteer):
    """Формирование нового описания задачи без удаленного волонтера."""
    description = ""

    for vol in issue.volunteers:
        if vol.id != volunteer.id:
            description += f"...{vol.description}..."
