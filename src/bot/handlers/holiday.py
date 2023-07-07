import datetime
import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.service.holiday import (
    check_data_is_valid_date, check_date_is_gt_than_now, date_to_str,
    get_user_holidays_dates, now_date_generator, now_date_str_generator,
    str_to_date,
)
from src.bot.handlers.state_constants import (
    ADD_HOLIDAY_DATES, BACK, CANCEL_HOLIDAY, ENDLESS, ENTER_HOLIDAY_MAIN,
    FEATURES, HOLIDAY, HOLIDAY_END, HOLIDAY_END_PATTERN, HOLIDAY_ENDLESS,
    HOLIDAY_NOW, HOLIDAY_START, HOLIDAY_START_PATTERN, INPUT_HOLIDAY_END,
    INPUT_HOLIDAY_START, SAVE_HOLIDAY, START_ENDLESS_HOLIDAY_NOW,
    STOP_HOLIDAY_NOW,
)
from src.core.db.db import get_async_session
from src.core.db.repository.volunteer_repository import crud_volunteer


class HolidayButtons:
    """Популярные кнопки раздела Отпуск."""

    manage_dates = [
        InlineKeyboardButton(
            text="Точная настройка дат отпуска",
            callback_data=ADD_HOLIDAY_DATES,
        )
    ]
    infinite_now = [
        InlineKeyboardButton(
            text="Уйти в бесконечный отпуск сегодня",
            callback_data=START_ENDLESS_HOLIDAY_NOW,
        )
    ]
    stop_today = [
        InlineKeyboardButton(
            text="Выйти из отпуска сегодня",
            callback_data=STOP_HOLIDAY_NOW,
        )
    ]
    cancel = [
        InlineKeyboardButton(
            text="Отменить отпуск",
            callback_data=CANCEL_HOLIDAY,
        )
    ]
    back_to_volonteer = [
        InlineKeyboardButton(
            text="Назад в управление профилем",
            callback_data=BACK,
        )
    ]
    back_to_holiday_main_screen = [
        InlineKeyboardButton(
            text="Назад в управление отпуском",
            callback_data=ENTER_HOLIDAY_MAIN,
        )
    ]


async def no_holiday_main_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, holiday_start, holiday_end) -> str:
    text = "У вас нет запланированого или действующего отпуска. Хотите оформить?"
    buttons = [
        HolidayButtons.infinite_now,
        HolidayButtons.manage_dates,
        HolidayButtons.back_to_volonteer,
    ]
    context.user_data[FEATURES][HOLIDAY_START] = holiday_start
    context.user_data[FEATURES][HOLIDAY_END] = holiday_end
    await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    return HOLIDAY


async def in_endless_holiday_main_screen(
    update: Update, context: ContextTypes.DEFAULT_TYPE, holiday_start, holiday_end
) -> str:
    text = f"Вы в бессрочном отпуске с {holiday_start}. Хотите изменить это?"
    buttons = [
        HolidayButtons.stop_today,
        HolidayButtons.manage_dates,
        HolidayButtons.back_to_volonteer,
    ]
    context.user_data[FEATURES][HOLIDAY_START] = holiday_start
    context.user_data[FEATURES][HOLIDAY_END] = holiday_end
    await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    return HOLIDAY


async def endless_planed_main_screen(
    update: Update, context: ContextTypes.DEFAULT_TYPE, holiday_start, holiday_end
) -> str:
    text = f"У вас запланирован бессрочный отпуск с {holiday_start}. Хотите изменить его?"

    buttons = [
        HolidayButtons.infinite_now,
        HolidayButtons.manage_dates,
        HolidayButtons.cancel,
        HolidayButtons.back_to_volonteer,
    ]
    context.user_data[FEATURES][HOLIDAY_START] = holiday_start
    context.user_data[FEATURES][HOLIDAY_END] = holiday_end
    await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    return HOLIDAY


async def in_finite_holiday_main_screen(
    update: Update, context: ContextTypes.DEFAULT_TYPE, holiday_start, holiday_end
) -> str:
    text = f"Вы в отпуске до {holiday_end}. Хотите изменить текущий отпуск?"
    buttons = [
        HolidayButtons.stop_today,
        HolidayButtons.infinite_now,
        HolidayButtons.manage_dates,
        HolidayButtons.back_to_volonteer,
    ]
    context.user_data[FEATURES][HOLIDAY_START] = holiday_start
    context.user_data[FEATURES][HOLIDAY_END] = holiday_end
    await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    return HOLIDAY


async def finite_planed_main_screen(
    update: Update, context: ContextTypes.DEFAULT_TYPE, holiday_start, holiday_end
) -> str:
    text = f"У вас запланирован отпуск с {holiday_start} по {holiday_end}. Хотите изменить его? "
    buttons = [
        HolidayButtons.infinite_now,
        HolidayButtons.manage_dates,
        HolidayButtons.cancel,
        HolidayButtons.back_to_volonteer,
    ]
    context.user_data[FEATURES][HOLIDAY_START] = holiday_start
    context.user_data[FEATURES][HOLIDAY_END] = holiday_end
    await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    return HOLIDAY


async def holiday_main_screen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> HOLIDAY:
    user_holiday_start, user_holiday_end = await get_user_holidays_dates(user_tg_id=update.effective_chat.id)
    if FEATURES not in context.user_data:
        context.user_data[FEATURES] = {}

    today = datetime.date.today()

    if user_holiday_start is None:
        return await no_holiday_main_screen(
            update,
            context,
            holiday_start=None,
            holiday_end=None,
        )

    if user_holiday_end == ENDLESS and user_holiday_start <= today:
        return await in_endless_holiday_main_screen(
            update,
            context,
            holiday_start=date_to_str(user_holiday_start),
            holiday_end=ENDLESS,
        )

    if user_holiday_end == ENDLESS and user_holiday_start > today:
        return await endless_planed_main_screen(
            update,
            context,
            holiday_start=date_to_str(user_holiday_start),
            holiday_end=ENDLESS,
        )

    if user_holiday_start <= today and user_holiday_end and user_holiday_end >= today:
        return await in_finite_holiday_main_screen(
            update,
            context,
            holiday_start=date_to_str(user_holiday_start),
            holiday_end=date_to_str(user_holiday_end),
        )
    if user_holiday_start > today and user_holiday_end:
        return await finite_planed_main_screen(
            update,
            context,
            holiday_start=date_to_str(user_holiday_start),
            holiday_end=date_to_str(user_holiday_end),
        )
    return await no_holiday_main_screen(
        update,
        context,
        holiday_start=None,
        holiday_end=None,
    )


async def cancel_holiday_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    text = "Отменяем отпуск?"
    buttons = [
        [InlineKeyboardButton(text="Верно", callback_data=STOP_HOLIDAY_NOW)],
        HolidayButtons.back_to_holiday_main_screen,
        HolidayButtons.back_to_volonteer,
    ]
    await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    return SAVE_HOLIDAY


async def endless_holiday_now_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    text = "Уходите в бесконечный отпуск прямо сейчас?"
    buttons = [
        [InlineKeyboardButton(text="Верно", callback_data=START_ENDLESS_HOLIDAY_NOW)],
        HolidayButtons.back_to_holiday_main_screen,
        HolidayButtons.back_to_volonteer,
    ]
    await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    return SAVE_HOLIDAY


async def endless_holiday_now_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    return await dates_save_to_db_and_send(update, context, now_date_generator(), None)


async def stop_holiday_today_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    text = "Выходите из отпуска прямо сейчас?"
    buttons = [
        [InlineKeyboardButton(text="Верно", callback_data=STOP_HOLIDAY_NOW)],
        HolidayButtons.back_to_holiday_main_screen,
        HolidayButtons.back_to_volonteer,
    ]
    await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    return SAVE_HOLIDAY


async def stop_holiday_today_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    return await dates_save_to_db_and_send(update, context, None, None)


async def manage_holiday_dates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    holiday_start = context.user_data[FEATURES].get(HOLIDAY_START, None)
    holiday_end = context.user_data[FEATURES].get(HOLIDAY_END, None)
    text = "Точная настройка дат отпуска"

    if holiday_start is not None:
        start_button_text = f"Начало отпуска {holiday_start}. Изменить"
        if holiday_end is None:
            end_button_text = "Ввести дату окончания отпуска"
        elif holiday_end == ENDLESS:
            end_button_text = "Бесконечный отпуск. Изменить"
        elif str_to_date(holiday_start) <= str_to_date(holiday_end):
            end_button_text = f"Окончание отпуска {holiday_end}. Изменить"

        else:
            end_button_text = f"Окончание отпуска {holiday_end}. Изменить"
            text = "У вас начало отпуска позже чем конец. "
            # ТУТ надо ПОДУМАТЬ
        buttons = [
            [InlineKeyboardButton(text=start_button_text, callback_data=HOLIDAY_START)],
            [InlineKeyboardButton(text=end_button_text, callback_data=HOLIDAY_END)],
        ]

    else:
        start_button_text = "Ввести дату начала отпуска"
        buttons = [
            [InlineKeyboardButton(text=start_button_text, callback_data=HOLIDAY_START)],
        ]

    buttons.extend(
        [
            HolidayButtons.back_to_holiday_main_screen,
            HolidayButtons.back_to_volonteer,
        ]
    )

    await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    return HOLIDAY


async def start_save_to_db_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE, holiday_start) -> str:
    session_generator = get_async_session()
    session = await session_generator.asend(None)
    user = await crud_volunteer.get_volunteer_by_telegram_id(update.effective_chat.id, session)
    data = {
        "holiday_start": holiday_start,
    }
    await crud_volunteer.update(user, data, session)
    if context.user_data[FEATURES].get(HOLIDAY_END, None) is None:
        return await manage_holiday_dates(update, context)
    return await holiday_main_screen(update, context)


async def end_save_to_db_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE, holiday_end) -> str:
    session_generator = get_async_session()
    session = await session_generator.asend(None)
    user = await crud_volunteer.get_volunteer_by_telegram_id(update.effective_chat.id, session)
    data = {
        "holiday_end": holiday_end,
    }
    await crud_volunteer.update(user, data, session)
    return await holiday_main_screen(update, context)


async def dates_save_to_db_and_send(
    update: Update, context: ContextTypes.DEFAULT_TYPE, holiday_start, holiday_end
) -> str:
    session_generator = get_async_session()
    session = await session_generator.asend(None)
    user = await crud_volunteer.get_volunteer_by_telegram_id(update.effective_chat.id, session)
    data = {
        "holiday_start": holiday_start,
        "holiday_end": holiday_end,
    }
    await crud_volunteer.update(user, data, session)
    return await holiday_main_screen(update, context)


async def ask_to_input_start_date(update: Update, context: ContextTypes.DEFAULT_TYPE, error_text=None) -> str:
    button_text = "С сегодняшнего дня"
    text = f"Введите дату начала отпуска в формате дд.мм.гггг или выберите '{button_text}'."
    if error_text is not None:
        text = error_text + text
    buttons = [
        [InlineKeyboardButton(text=button_text, callback_data=HOLIDAY_NOW)],
        HolidayButtons.back_to_holiday_main_screen,
        HolidayButtons.back_to_volonteer,
    ]
    await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    return INPUT_HOLIDAY_START


async def ask_to_input_end_date(update: Update, context: ContextTypes.DEFAULT_TYPE, error_text=None) -> str:
    button_text = "Бессрочно"
    text = f"Введите дату окончания отпуска в формате дд.мм.гггг или выберите '{button_text}'."
    if error_text is not None:
        text = error_text + text
    buttons = [
        [InlineKeyboardButton(text=button_text, callback_data=HOLIDAY_ENDLESS)],
        HolidayButtons.back_to_holiday_main_screen,
        HolidayButtons.back_to_volonteer,
    ]
    await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    return INPUT_HOLIDAY_END


async def parse_start_date_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_input = update.message.text
    if not check_data_is_valid_date(user_input):
        return await ask_to_input_start_date(
            update, context, error_text=f"Вы ввели {user_input}. Я не могу распознать это как дату!"
        )
    if not check_date_is_gt_than_now(user_input):
        return await ask_to_input_start_date(
            update, context, error_text="Вы ввели дату из прошлого. Я не могу оформить отпуск задним числом."
        )

    data = HOLIDAY_START + "=" + user_input

    buttons = [
        [InlineKeyboardButton(text="Верно", callback_data=data)],
        [InlineKeyboardButton(text="Изменить начало отпуска", callback_data=HOLIDAY_START)],
        HolidayButtons.back_to_holiday_main_screen,
        HolidayButtons.back_to_volonteer,
    ]
    await update.message.reply_text(text=f"Отпуск начнется {user_input}", reply_markup=InlineKeyboardMarkup(buttons))
    return INPUT_HOLIDAY_START


async def parse_end_date_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_input = update.message.text
    if not check_data_is_valid_date(user_input):
        return await ask_to_input_start_date(
            update, context, error_text=f"Вы ввели {user_input}. Я не могу распознать это как дату!"
        )
    if not check_date_is_gt_than_now(user_input):
        return await ask_to_input_start_date(
            update, context, error_text="Вы ввели дату из прошлого. Я не могу оформить отпуск задним числом."
        )
    # ТУТ НУЖНА проверка что конец больше старта
    # если нет то предлагаем изменить и конец и начало

    data = HOLIDAY_END + "=" + user_input

    buttons = [
        [InlineKeyboardButton(text="Верно", callback_data=data)],
        [InlineKeyboardButton(text="Изменить конец отпуска", callback_data=HOLIDAY_END)],
        HolidayButtons.back_to_holiday_main_screen,
        HolidayButtons.back_to_volonteer,
    ]
    await update.message.reply_text(text=f"Отпуск закончится {user_input}", reply_markup=InlineKeyboardMarkup(buttons))
    return INPUT_HOLIDAY_END


async def handle_autodate_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_input = now_date_str_generator()
    data = HOLIDAY_START + "=" + user_input
    buttons = [
        [InlineKeyboardButton(text="Верно", callback_data=data)],
        [InlineKeyboardButton(text="Изменить начало отпуска", callback_data=HOLIDAY_START)],
        HolidayButtons.back_to_holiday_main_screen,
        HolidayButtons.back_to_volonteer,
    ]
    text = f"Отпуск начнется {user_input}"
    await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    return INPUT_HOLIDAY_START


async def handle_autodate_end_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    buttons = [
        [InlineKeyboardButton(text="Верно", callback_data=HOLIDAY_ENDLESS)],
        [InlineKeyboardButton(text="Изменить конец отпуска", callback_data=HOLIDAY_END)],
        HolidayButtons.back_to_holiday_main_screen,
        HolidayButtons.back_to_volonteer,
    ]
    text = "Отпуск без конца?"
    await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    return INPUT_HOLIDAY_END


async def save_start_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    data = update.callback_query.data
    data = re.match(HOLIDAY_START_PATTERN, data)
    date = data.group(HOLIDAY_START)
    context.user_data[FEATURES][HOLIDAY_START] = date
    date = str_to_date(date)
    # тут наверно  нужна проверка
    return await start_save_to_db_and_send(update, context, holiday_start=date)


async def save_end_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    data = update.callback_query.data
    data = re.match(HOLIDAY_END_PATTERN, data)
    date = data.group(HOLIDAY_END)
    context.user_data[FEATURES][HOLIDAY_END] = date
    date = str_to_date(date)
    # тут наверно  нужна проверка
    return await end_save_to_db_and_send(update, context, holiday_end=date)


async def endless_holiday_end_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    text = "Выбрать бесконечный отпуск?"
    buttons = [
        [InlineKeyboardButton(text="Верно", callback_data=HOLIDAY_ENDLESS)],
        HolidayButtons.back_to_holiday_main_screen,
        HolidayButtons.back_to_volonteer,
    ]
    await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    return SAVE_HOLIDAY


async def endless_holiday_end_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    context.user_data[FEATURES][HOLIDAY_END] = ENDLESS
    if context.user_data[FEATURES][HOLIDAY_START] is not None:
        return await dates_save_to_db_and_send(
            update,
            context,
            holiday_start=str_to_date(context.user_data[FEATURES][HOLIDAY_START]),
            holiday_end=None,
        )

    return await dates_save_to_db_and_send(
        update,
        context,
        holiday_start=now_date_generator(),
        holiday_end=None,
    )
