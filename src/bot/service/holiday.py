from src.api.constants import VOLUNTEER_STATUS
from src.core.db.model import Volunteer


def chek_and_update_holiday_status(volunteer: Volunteer, issue):
    if volunteer.is_banned:
        return
    transitions = issue.transitions.get_all()
    transitions_ids = [transition.id for transition in transitions]
    if get_volunteer_is_in_vocation(volunteer):
        if VOLUNTEER_STATUS.otpusk.value in transitions_ids:
            return issue.transitions[VOLUNTEER_STATUS.otpusk.value].execute()
        return
    if VOLUNTEER_STATUS.open.value in transitions_ids:
        return issue.transitions[VOLUNTEER_STATUS.open.value].execute()


def get_volunteer_is_in_vocation(volunteer: Volunteer) -> bool:
    if volunteer.holiday_start is not None:
        return True
    return False
