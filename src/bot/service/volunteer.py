from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.handlers.state_constants import (
    FIRST_NAME,
    GEOM,
    LAST_NAME,
    LATITUDE,
    LONGITUDE,
    SPECIFY_ACTIVITY_RADIUS,
    SPECIFY_CAR_AVAILABILITY,
    SPECIFY_CITY,
    SPECIFY_PHONE_PERMISSION,
    TELEGRAM_ID,
    TELEGRAM_USERNAME,
    VOLUNTEER,
)
from src.api.tracker import client
from src.core.db.db import get_async_session
from src.core.db.model import Volunteer
from src.core.db.repository.volunteer_repository import crud_volunteer


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


async def get_is_volunteer_exists(telegram_id: int) -> bool:
    """Проверяет существует ли волонтер с указанным id в базе"""
    session_generator = get_async_session()
    session = await session_generator.asend(None)
    return await crud_volunteer.get_exist_by_attribute(TELEGRAM_ID, telegram_id, session)


def volunteers_description(volunteers):
    if not volunteers:
        return "\n---- \n\nВолонтёров поблизости не нашлось"
    description = "\n---- \n\nВолонтёры поблизости\n\n"
    description_add_hascar = ""
    description_add_nocar = ""
    for volunteer in volunteers:
        volunteer_description = (
            f"https://t.me/{volunteer.telegram_username}, {volunteer.city}\n{volunteer.ticketID}\n\n"
        )
        if volunteer.has_car:
            description_add_hascar += volunteer_description
        else:
            description_add_nocar += volunteer_description
    if description_add_hascar:
        description += "* с авто:\n\n" + description_add_hascar
    if description_add_nocar:
        description += "* без авто:\n\n" + description_add_nocar
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
    data.pop(SPECIFY_CITY, None)
    return data


async def create_or_update_volunteer(
        volunteer_data: dict, volunteer_is_exists: bool, session) -> tuple[Optional[Volunteer], Optional[str]]:
    """Создает или обновляет данные волонтера"""
    if volunteer_is_exists:
        volunteer = await crud_volunteer.get_volunteer_by_telegram_id(volunteer_data[TELEGRAM_ID], session)
        old_ticket_id = volunteer.ticketID
        if volunteer.is_banned:
            return None, old_ticket_id
        for attr in set(volunteer_data.keys()):
            if getattr(volunteer, attr) == volunteer_data[attr]:
                del volunteer_data[attr]
        if not volunteer_data:
            return None, old_ticket_id
        volunteer = await update_volunteer(volunteer, volunteer_data, session)
    else:
        volunteer = await create_volunteer(volunteer_data, session)
        old_ticket_id = None
    return volunteer, old_ticket_id


def get_tracker(volunteer: Volunteer, old_ticket_id: str):
    user_name = volunteer.telegram_username
    if user_name is None:
        user_name = "Никнейм скрыт"
    summary = f"{user_name} - {volunteer.full_address}"
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
    if old_ticket_id:
        description += f"Старый тикет: {old_ticket_id}"
    return client.issues.create(
        queue=VOLUNTEER,
        summary=summary,
        description=description,
    )
