from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.api.tracker import client
from src.bot.handlers.start import start
from src.bot.handlers.state_constants import (
    ACTIVITY_RADIUS,
    ADDING_VOLUNTEER,
    BACK,
    CAR_COMMAND,
    CITY,
    CITY_COMMAND,
    CITY_INPUT,
    CURRENT_FEATURE,
    END,
    FEATURES,
    FIRST_NAME,
    GEOM,
    LAST_NAME,
    LATITUDE,
    LONGITUDE,
    RADIUS_COMMAND,
    SAVE,
    SECOND_LEVEL_TEXT,
    SELECTING_OVER,
    SPECIFY_ACTIVITY_RADIUS,
    SPECIFY_CAR_AVAILABILITY,
    SPECIFY_CITY,
    SPECIFY_PHONE_PERMISSION,
    START_OVER,
    TELEGRAM_ID,
    TELEGRAM_USERNAME,
    TYPING_CITY,
    VOLUNTEER,
)
from src.bot.service.dadata import get_fields_from_dadata
from src.bot.service.save_new_user import check_user_in_db, create_new_user
from src.bot.service.save_tracker_id import save_tracker_id
from src.bot.service.volunteer import check_volunteer_in_db, create_volunteer, update_volunteer
from src.core.db.db import get_async_session
from src.core.db.repository.volunteer_repository import crud_volunteer


async def add_volunteer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Меню регистрации волонтёра."""
    text = (
        "Для регистрации волонтером вам надо указать:\n"
        "- Свой адрес, можно без квартиры, для удобства расчетов расстояния;\n"
        "- Расстояние, на которое ты готов выезжать;\n"
        "- Наличие автомобиля, и готовность задействовать его;\n"
        "- [Опционально] Номер телефона для связи."
    )

    buttons = [
        [
            InlineKeyboardButton(text="Указать свой адрес", callback_data=SPECIFY_CITY),
        ],
        [
            InlineKeyboardButton(text="Указать радиус активности", callback_data=SPECIFY_ACTIVITY_RADIUS),
        ],
        [
            InlineKeyboardButton(text="Указать наличие автомобиля", callback_data=SPECIFY_CAR_AVAILABILITY),
        ],
        [
            InlineKeyboardButton(text="Указать номер телефона", callback_data=SPECIFY_PHONE_PERMISSION),
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
            buttons.append([InlineKeyboardButton(text="Отправить заявку", callback_data=SAVE)])
            keyboard = InlineKeyboardMarkup(buttons)
        if update.message is not None:
            await update.message.reply_text(text=SECOND_LEVEL_TEXT, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        else:
            await update.callback_query.edit_message_text(
                text=SECOND_LEVEL_TEXT, reply_markup=keyboard, parse_mode=ParseMode.HTML
            )

    context.user_data[START_OVER] = False
    return ADDING_VOLUNTEER


async def end_second_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Возврат к главному меню."""
    context.user_data[START_OVER] = True
    await start(update, context)

    return END


async def ask_user_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Предложить пользователю ввести свой номер телефона."""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = "Укажите свой номер телефона:"
    button = [[InlineKeyboardButton(text="Назад", callback_data=BACK)]]
    keyboard = InlineKeyboardMarkup(button)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_OVER


async def save_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Сохранение комментария"""
    user_data = context.user_data
    user_data[FEATURES][user_data[CURRENT_FEATURE]] = update.message.text
    user_data[START_OVER] = True

    return await add_volunteer(update, context)


async def ask_for_input_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Предложить пользователю ввести данные о населенном пункте."""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = "Укажите свой адрес:"
    button = [[InlineKeyboardButton(text="Назад", callback_data=BACK)]]
    keyboard = InlineKeyboardMarkup(button)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return TYPING_CITY


async def handle_city_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Обработчик данных о населенном пункте с выводом возможных вариантов."""
    user_input = update.message.text
    address = get_fields_from_dadata(user_input)
    if address is not None:
        text = (
            f"Это правильный адрес: {address['full_address']}? "
            'Если адрес не правильный, то выберите "Нет" и укажите более подробный вариант адреса, '
            "а мы постараемся определить его правильно!"
        )
        context.user_data[FEATURES] |= address

        buttons = [
            [
                InlineKeyboardButton(text="Да", callback_data=CITY_COMMAND),
                InlineKeyboardButton(text="Нет", callback_data=CITY_INPUT),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data=BACK),
            ],
        ]

        keyboard = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(text=text, reply_markup=keyboard)

    else:
        chat_text = "Не нашли такой адрес. Пожалуйста, укажи адрес подробнее:"

        buttons = [
            [
                InlineKeyboardButton(text="Указать адрес заново", callback_data=CITY_INPUT),
                InlineKeyboardButton(text="Назад", callback_data=BACK),
            ]
        ]

        keyboard = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(text=chat_text, reply_markup=keyboard)

    return SELECTING_OVER


async def handle_radius_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Обработчик данных о радиусе действия."""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = (
        "Выберите из представленных вариантов расстояние, на которое вы готовы "
        "выезжать. Радиусы выезда указаны в километрах:"
    )

    buttons = []

    for ranges in ACTIVITY_RADIUS:
        button_row = []
        for radius in ranges:
            data = RADIUS_COMMAND + str(radius)
            button_row.append(InlineKeyboardButton(text=radius, callback_data=data))
        buttons.append(button_row)

    button = [InlineKeyboardButton(text="Назад", callback_data=BACK)]
    buttons.append(button)

    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_OVER


async def handle_car_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Обработчик данных о наличии автомобиля."""
    text = "Пожалуйста, укажите наличие автомобиля и готовность задействовать его"
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    buttons = [
        [
            InlineKeyboardButton(text="Да", callback_data=CAR_COMMAND + "Yes"),
            InlineKeyboardButton(text="Нет", callback_data=CAR_COMMAND + "No"),
        ],
        [InlineKeyboardButton(text="Назад", callback_data=BACK)],
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
    radius = user_data[SPECIFY_ACTIVITY_RADIUS][7:]
    car = user_data[SPECIFY_CAR_AVAILABILITY][4:]
    if SPECIFY_PHONE_PERMISSION in user_data:
        phone = user_data[SPECIFY_PHONE_PERMISSION]
    else:
        phone = "Не указан"
    user_data[GEOM] = f"POINT({user_data[LONGITUDE]} {user_data[LATITUDE]})"
    user_data[SPECIFY_ACTIVITY_RADIUS] = int(radius) * 1000
    user_data[SPECIFY_CAR_AVAILABILITY] = car
    user_data[SPECIFY_PHONE_PERMISSION] = phone
    user_data[TELEGRAM_ID] = update.effective_user.id
    user_data[TELEGRAM_USERNAME] = update.effective_user.username
    user_data[FIRST_NAME] = update.effective_user.first_name
    user_data[LAST_NAME] = update.effective_user.last_name
    if SPECIFY_CITY in user_data:
        del user_data[SPECIFY_CITY]
    if user_data[SPECIFY_CAR_AVAILABILITY] == "Yes":
        user_data[SPECIFY_CAR_AVAILABILITY] = True
    else:
        user_data[SPECIFY_CAR_AVAILABILITY] = False
    user = {}
    user[TELEGRAM_ID] = user_data[TELEGRAM_ID]
    user[TELEGRAM_USERNAME] = user_data[TELEGRAM_USERNAME]
    session_generator = get_async_session()
    session = await session_generator.asend(None)
    old_user = await check_user_in_db(user_data[TELEGRAM_ID], session)
    if not old_user:
        await create_new_user(user, session)
    if old_user and old_user.is_banned:
        await start(update, context)
        return END
    old_volunteer = await check_volunteer_in_db(user_data[TELEGRAM_ID], session)
    if old_volunteer:
        if (
            old_volunteer.full_address == user_data["full_address"]
            and old_volunteer.has_car == user_data[SPECIFY_CAR_AVAILABILITY]
            and old_volunteer.radius == int(radius) * 1000
            and old_volunteer.phone == phone
        ):
            await start(update, context)
            return END
        else:
            await update_volunteer(old_volunteer, user_data, session)
    else:
        await create_volunteer(user_data, session)
    user_name = user_data[TELEGRAM_USERNAME]
    if user_name is None:
        user_name = "Никнейм скрыт"
    summary = f"{user_name} - {user_data['full_address']}"
    description = f"""
    Ник в телеграмме: {user_name}
    Адрес: {user_data['full_address']}
    Наличие машины: {car}
    Радиус выезда: {radius}
    Номер телефона: {phone}
    """
    tracker = client.issues.create(
        queue=VOLUNTEER,
        summary=summary,
        description=description,
    )
    await save_tracker_id(crud_volunteer, tracker.key, user_data[TELEGRAM_ID], session)
    await start(update, context)
    return END


def check_data(user_data):
    if (CITY in user_data and SPECIFY_ACTIVITY_RADIUS in user_data) and SPECIFY_CAR_AVAILABILITY in user_data:
        return True
    else:
        return False
