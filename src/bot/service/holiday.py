import datetime
import re

from src.bot.handlers.state_constants import ENDLESS
from src.core.db.db import get_async_session
from src.core.db.repository.volunteer_repository import crud_volunteer

DATE_FORMAT = "%d.%m.%Y"


async def get_user_holidays_dates(user_tg_id):
    session_generator = get_async_session()
    session = await session_generator.asend(None)
    user = await crud_volunteer.get_volunteer_by_telegram_id(user_tg_id, session)
    if user.holiday_start:
        user_holiday_start = user.holiday_start.date()
    else:
        user_holiday_start = None
    if user.holiday_end:
        user_holiday_end = user.holiday_end.date()
    elif user_holiday_start:
        user_holiday_end = ENDLESS
    else:
        user_holiday_end = None
    return user_holiday_start, user_holiday_end


def check_data_is_valid_date(data: str) -> bool:
    pattern = re.compile(r"^(?P<day>\d\d).(?P<month>\d\d).(?P<year>\d\d\d\d)")
    date_match = re.match(pattern, data)
    if not date_match:
        return False
    day = int(date_match.group("day"))
    month = int(date_match.group("month"))
    year = int(date_match.group("year"))
    if not (day and month and year):
        return False
    if month > 12:
        return False
    if day > 31:
        return False
    if month in [4, 6, 9, 11] and day > 30:
        return False
    if year % 4 > 0 and month == 2 and day > 28:
        return False
    return True


def check_date_is_gt_than_now(data: str) -> bool:
    today = now_date_generator()
    date = datetime.datetime.strptime(data, DATE_FORMAT).date()
    if date < today:
        return False
    return True


def now_date_str_generator() -> str:
    today = now_date_generator()
    return today.strftime(DATE_FORMAT)


def now_date_generator():
    return datetime.date.today()


def date_to_str(date: datetime.datetime) -> str | None:
    if date is not None:
        return date.strftime(DATE_FORMAT)
    return None


def str_to_date(data: str) -> datetime.datetime:
    if data == ENDLESS:
        return None
    if data:
        return datetime.datetime.strptime(data, DATE_FORMAT).date()
    return None
