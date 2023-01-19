from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.address.address_api import mock_get_city_name
from bot.handlers.start import start
from bot.handlers.state_constants import (
    ACTIVITY_RADIUS,
    ADDING_VOLUNTEER,
    CAR_COMMAND,
    CITY_COMMAND,
    CURRENT_FEATURE,
    END,
    FEATURES,
    RADIUS_COMMAND,
    SELECTING_OVER,
    SPECIFY_ACTIVITY_RADIUS,
    SPECIFY_CAR_AVAILABILITY,
    SPECIFY_CITY,
    START_OVER,
    TYPING_CITY,
)


async def add_volunteer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Меню регистрации волонтёра."""
    text = (
        "Для регистрации волонтером тебе надо указать:"
        "\t- свой населенный пункт;"
        "\t- Расстояние, на которое ты готов выезжать;"
        "\t- Наличие автомобиля, и готовность задействовать его."
    )
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
    text = "Напиши населенный пункт, я поищи его в базе."

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)

    return TYPING_CITY


async def handle_city_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Обработчик данных о населенном пункте с выводом возможных вариантов."""
    user_input = update.message.text
    text = "Пожалуйста, выбери город из представленных"
    possible_cities = mock_get_city_name(user_input)
    buttons = []

    for city in possible_cities:
        data = CITY_COMMAND + city
        buttons.append(
            [
                InlineKeyboardButton(text=city, callback_data=data),
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
