from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from yandex_tracker_client.exceptions import NotFound

from src.api.tracker import client
from src.bot.handlers.state_constants import (
    ADDRESS_INPUT,
    FIRST_NAME,
    GEOM,
    LAST_NAME,
    LATITUDE,
    LONGITUDE,
    SPECIFY_ACTIVITY_RADIUS,
    SPECIFY_CAR_AVAILABILITY,
    SPECIFY_PHONE_PERMISSION,
    TELEGRAM_ID,
    TELEGRAM_USERNAME,
    VOLUNTEER,
)
from src.core.db.model import Volunteer
from src.core.db.repository.volunteer_repository import crud_volunteer

VOLUNTEER_UPDATE = "https://t.me/{tlg_username}, \n{ticketID}\n\n"


class VolunteerCreate(BaseModel):
    telegram_id = int
    city = str
    full_address = str
    radius = int
    has_car = str
    latitude = float
    longitude = float
    geometry = str
    telegram_username = Optional[str]
    first_name = Optional[str]
    last_name = Optional[str]
    phone = Optional[str]
    birthday = Optional[datetime.date]
    is_banned = Optional[bool]
    ticketID = Optional[str]

    class Config:
        arbitrary_types_allowed = True


async def create_volunteer(data: VolunteerCreate, session: AsyncSession):
    return await crud_volunteer.create(data, session)


async def update_volunteer(db_obj: Volunteer, data: VolunteerCreate, session: AsyncSession):
    return await crud_volunteer.update(db_obj, data, session)


def volunteers_description(volunteers: list[Volunteer]):
    description = "\n---- \n\nВолонтёры поблизости:\n\n"
    if not volunteers:
        description += "\n\nВолонтёров поблизости не нашлось."
        return description
    for volunteer in volunteers:
        description += VOLUNTEER_UPDATE.format(
            tlg_username=volunteer.telegram_username,
            ticketID=volunteer.ticketID
        )
    return description


def volunteer_data_preparation(telegram_id: int, username: str, first_name: str, last_name: str, data: dict) -> dict:
    """Подготовка данных волонтера"""
    data[TELEGRAM_ID] = telegram_id
    data[TELEGRAM_USERNAME] = username
    data[FIRST_NAME] = first_name
    data[LAST_NAME] = last_name
    if LONGITUDE in data and LATITUDE in data:
        data[GEOM] = f"POINT({data[LONGITUDE]} {data[LATITUDE]})"
    if SPECIFY_ACTIVITY_RADIUS in data:
        data[SPECIFY_ACTIVITY_RADIUS] = int(data[SPECIFY_ACTIVITY_RADIUS][7:]) * 1000
    if SPECIFY_CAR_AVAILABILITY in data:
        data[SPECIFY_CAR_AVAILABILITY] = True if data[SPECIFY_CAR_AVAILABILITY][4:] == "Да" else False
    if SPECIFY_PHONE_PERMISSION in data:
        data[SPECIFY_PHONE_PERMISSION] = data[SPECIFY_PHONE_PERMISSION][6:]
    data.pop(ADDRESS_INPUT, None)
    return data


async def check_and_update_volunteer(
    volunteer_data: dict, session: AsyncSession
) -> tuple[Optional[Volunteer], Optional[str]]:
    """Проверяет не забанен ли волонтер, есть ли данные для обновления"""
    volunteer = await crud_volunteer.get_volunteer_by_telegram_id(volunteer_data[TELEGRAM_ID], session)
    old_ticket_id = volunteer.ticketID
    for attr in set(volunteer_data.keys()):
        if getattr(volunteer, attr) == volunteer_data[attr]:
            del volunteer_data[attr]
    if not volunteer_data:
        return None, old_ticket_id
    volunteer = await update_volunteer(volunteer, volunteer_data, session)
    return volunteer, old_ticket_id


def form_description(volunteer: Volunteer):
    user_name = volunteer.telegram_username
    if volunteer.telegram_username is None:
        user_name = "Никнейм скрыт"
    description = f"""
        Ник в телеграмме: {user_name}
        Адрес: {volunteer.full_address}
        Наличие машины: {"Да" if volunteer.has_car else "Нет"}
        Радиус выезда: {volunteer.radius / 1000} км
        """
    if volunteer.phone is None:
        description += "Номер телефона: Не указан\n"
    else:
        description += f"Номер телефона: {volunteer.phone}\n"
    return description


def form_summary(volunteer: Volunteer):
    user_name = volunteer.telegram_username
    if user_name is None:
        user_name = "Никнейм скрыт"
    return f"{user_name} - {volunteer.full_address}"


def create_volunteer_ticket(volunteer: Volunteer):
    return client.issues.create(
        queue=VOLUNTEER,
        summary=form_summary(volunteer),
        description=form_description(volunteer),
    )


def update_volunteer_ticket(volunteer: Volunteer, ticket_id: str):
    try:
        issue = client.issues[ticket_id]
        return issue.update(
            summary=form_summary(volunteer),
            description=form_description(volunteer),
        )
    except NotFound:
        return create_volunteer_ticket(volunteer)
