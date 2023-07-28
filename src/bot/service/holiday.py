from yandex_tracker_client.objects import Resource

from bot.handlers.loggers import logger
from src.api.constants import VOLUNTEER_STATUS
from src.api.tracker import client
from src.core.db.model import Volunteer


def check_and_update_holiday_status(volunteer: Volunteer, issue: Resource) -> Resource:
    """Проверяет и обновляет статус волонтера. Если статус меняется то обновляет issue"""
    if volunteer.is_banned:
        return
    current_status = issue.status.key
    transitions = issue.transitions.get_all()
    transitions_ids = [transition.id for transition in transitions]
    if get_volunteer_is_in_holiday(volunteer):
        if VOLUNTEER_STATUS.otpusk.value in transitions_ids:
            issue.transitions[VOLUNTEER_STATUS.otpusk.value].execute()
            return client.issues[issue.id]
        if current_status == VOLUNTEER_STATUS.otpusk.value:
            return issue
        logger.error(f"Status {VOLUNTEER_STATUS.otpusk.value} not found in VOLUNTEER statuses")
        return issue
    if VOLUNTEER_STATUS.open.value in transitions_ids:
        issue.transitions[VOLUNTEER_STATUS.open.value].execute()
        return client.issues[issue.id]
    if current_status == VOLUNTEER_STATUS.open.value:
        return issue
    logger.error(f"Status {VOLUNTEER_STATUS.open.value} not found in VOLUNTEER statuses")
    return issue


def get_volunteer_is_in_holiday(volunteer: Volunteer) -> bool:
    if volunteer.holiday_start is not None:
        return True
    return False
