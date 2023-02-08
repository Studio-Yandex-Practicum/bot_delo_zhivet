from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.api.tracker import client
from src.bot.handlers.start import start
from src.bot.handlers.state_constants import (
    ACTIVITY_RADIUS,
    ADDING_VOLUNTEER,
    CAR_COMMAND,
    CITY_COMMAND,
    CURRENT_FEATURE,
    CURRENT_LEVEL,
    END,
    FEATURES,
    FIRST_NAME,
    LAST_NAME,
    RADIUS_COMMAND,
    SAVE,
    SELECTING_OVER,
    SPECIFY_ACTIVITY_RADIUS,
    SPECIFY_CAR_AVAILABILITY,
    SPECIFY_CITY,
    START_OVER,
    TELEGRAM_ID,
    TELEGRAM_USERNAME,
    TYPING_CITY,
    VOLUNTEER,
)
from src.bot.service.save_new_user import create_new_user
from src.bot.service.save_tracker_id import save_tracker_id_volunteer
from src.bot.service.volunteer import create_new_volunteer
from src.core.db.db import get_async_session


async def add_volunteer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Меню регистрации волонтёра."""
    text = (
        "Для регистрации волонтером тебе надо указать:"
        "\t- свой населенный пункт;"
        "\t- Расстояние, на которое ты готов выезжать;"
        "\t- Наличие автомобиля, и готовность задействовать его."
    )
    level = update.callback_query.data
    context.user_data[CURRENT_LEVEL] = level

    buttons = [
        [
            InlineKeyboardButton(text="Указать город", callback_data=SPECIFY_CITY),
        ],
        [
            InlineKeyboardButton(text="Указать радиус активности", callback_data=SPECIFY_ACTIVITY_RADIUS),
        ],
        [
            InlineKeyboardButton(text="Указать наличие автомобиля", callback_data=SPECIFY_CAR_AVAILABILITY),
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if not context.user_data.get(START_OVER):
        context.user_data[FEATURES] = {}

        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        if check_data(context.user_data[FEATURES]) is True:
            buttons.append([InlineKeyboardButton(text="Сохранить и выйти", callback_data=SAVE)])
            keyboard = InlineKeyboardMarkup(buttons)
        text = "Понял-принял!. Выбери следующую опцию"
        if update.message is not None:
            await update.message.reply_text(text=text, reply_markup=keyboard)
        else:
            await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return ADDING_VOLUNTEER


async def end_second_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Возврат к главному меню."""
    context.user_data[START_OVER] = True
    await start(update, context)

    return END


async def ask_for_input_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Предложить пользователю ввести данные о населенном пункте."""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = "Укажите свой адрес."

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)

    return TYPING_CITY


async def handle_city_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Обработчик данных о населенном пункте с выводом возможных вариантов."""
    user_input = update.message.text
    text = "Пожалуйста, выбери город из представленных"
    buttons = []

    data = CITY_COMMAND + user_input
    buttons.append(
        [
            InlineKeyboardButton(text=user_input, callback_data=data),
        ]
    )

    keyboard = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(text=text, reply_markup=keyboard)

    return SELECTING_OVER


async def handle_radius_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Обработчик данных о радиусе действия."""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = "Пожалуйста, выбери радиус из представленных"

    buttons = []

    for ranges in ACTIVITY_RADIUS:
        button_row = []
        for radius in ranges:
            data = RADIUS_COMMAND + str(radius)
            button_row.append(InlineKeyboardButton(text=radius, callback_data=data))
        buttons.append(button_row)

    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_OVER


async def handle_car_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Обработчик данных о наличии автомобиля."""
    text = "Пожалуйста, укажи наличие автомобиля и готовность задействовать его"
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    buttons = [
        [
            InlineKeyboardButton(text="Да", callback_data=CAR_COMMAND + "Yes"),
            InlineKeyboardButton(text="Нет", callback_data=CAR_COMMAND + "No"),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_OVER


async def save_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Сохранение данных в контексте."""

    city = update.callback_query.data

    user_data = context.user_data
    user_data[FEATURES][user_data[CURRENT_FEATURE]] = city

    user_data[START_OVER] = True

    return await add_volunteer(update, context)


async def save_and_exit_volunteer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Сохранение данных в базу и отправка в трекер"""
    context.user_data[START_OVER] = True
    user_data = context.user_data[FEATURES]
    city = user_data[SPECIFY_CITY][5:]
    radius = user_data[SPECIFY_ACTIVITY_RADIUS][7:]
    car = user_data[SPECIFY_CAR_AVAILABILITY][4:]
    user_data[SPECIFY_CITY] = city
    user_data[SPECIFY_ACTIVITY_RADIUS] = int(radius)
    user_data[SPECIFY_CAR_AVAILABILITY] = car
    user_data[TELEGRAM_ID] = update.effective_user.id
    user_data[TELEGRAM_USERNAME] = update.effective_user.username
    user_data[FIRST_NAME] = update.effective_user.first_name
    user_data[LAST_NAME] = update.effective_user.last_name
    session_generator = get_async_session()
    session = await session_generator.asend(None)
    await create_new_user(user_data[TELEGRAM_ID], session)
    await create_new_volunteer(user_data, session)
    summary = f"{user_data[TELEGRAM_USERNAME]} - {city}"
    description = f"""
    Ник в телеграмме: {user_data[TELEGRAM_USERNAME]}
    город: {city}
    наличие машины: {car}
    радиус выезда{radius}
    """
    client.issues.create(
        queue=VOLUNTEER,
        summary=summary,
        description=description,
    )
    await save_tracker_id_volunteer(summary, user_data[TELEGRAM_ID], session)
    await start(update, context)
    return END


def check_data(user_data):
    if (SPECIFY_CITY in user_data and SPECIFY_ACTIVITY_RADIUS in user_data) and SPECIFY_CAR_AVAILABILITY in user_data:
        return True
    else:
        return False
