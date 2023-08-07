from time import sleep

from sqlalchemy.ext.asyncio import AsyncSession
from yandex_tracker_client.exceptions import TrackerServerError

from src.api.tracker import client
from src.bot.handlers.state_constants import POLLUTION, SOCIAL
from src.core.db.model import Volunteer
from src.core.db.repository.volunteer_repository import crud_volunteer

VOLUNTEER_UPDATE = "https://t.me/{tlg_username}, \n{ticketID}\n\n"


def get_issues_with_statuses(
    queues: list = [POLLUTION, SOCIAL],
    statuses: list = ['OPEN']
):
    '''Функция возвращает открытые задачи и их ключи из трекера'''
    issues = client.issues.find(
        filter=dict(queue=queues, status=statuses)
    )
    issues_keys = [issue.key for issue in issues]
    return issues, issues_keys


async def processing_volunteer(
    new_volunteer: Volunteer,
    session: AsyncSession,
    old_volunteer: Volunteer = None
) -> None:
    '''
    Функция обновляет задачи при создании нового волонтера или
    смене им радиуса или адреса
    '''
    issues, issues_keys = get_issues_with_statuses()
    if old_volunteer:
        old_issues_keys = await crud_volunteer.get_issues_in_radius(
            old_volunteer, session
        )
        new_issues_keys = await crud_volunteer.get_issues_in_radius(
            new_volunteer, session
        )
        to_delete = [
            issue for issue in issues
            if issue.key
            in (set(old_issues_keys) - set(new_issues_keys)) & set(issues_keys)
        ]
        to_add = [
            issue for issue in issues
            if issue.key
            in (set(new_issues_keys) - set(old_issues_keys)) & set(issues_keys)
        ]
        add_new_volunteer(new_volunteer, to_add)
        delete_volunteer_from_issues(old_volunteer, to_delete)
    else:
        new_issues_keys = await crud_volunteer.get_issues_in_radius(
            new_volunteer, session
        )
        issues = [
            issue for issue in issues
            if issue.key in (set(new_issues_keys) & set(issues_keys))
        ]
        add_new_volunteer(new_volunteer, issues)


def issues_updater(issues: list) -> None:
    '''Фукнция для обновления задач в трекере'''
    while issues:
        for issue in issues:
            try:
                issue.update(description=issue.description)
                issues.remove(issue)
            except TrackerServerError:
                sleep(30)
            except Exception:
                issues.remove(issue)
                pass  # нужно доработать реакцию на сбой трекера


def add_new_volunteer(
    volunteer: Volunteer,
    issues: list
) -> None:
    '''Функция добавляет волонтера в описание задачи'''
    for issue in issues:
        issue.description = issue.description.replace(
            "\n\nВолонтёров поблизости не нашлось.", ''
        )
        issue.description += VOLUNTEER_UPDATE.format(
            tlg_username=volunteer.telegram_username,
            ticketID=volunteer.ticketID
        )
    issues_updater(issues)


def delete_volunteer_from_issues(
    volunteer: Volunteer,
    issues: list
) -> None:
    '''Функция удаляет запись волонтера из описания задачи'''
    for issue in issues:
        issue.description = issue.description.replace(
            VOLUNTEER_UPDATE.format(
                tlg_username=volunteer.telegram_username,
                ticketID=volunteer.ticketID
            ), ''
        )
        if 'https://t.me/' not in issue.description:
            issue.description += "\n\nВолонтёров поблизости не нашлось."
    issues_updater(issues)