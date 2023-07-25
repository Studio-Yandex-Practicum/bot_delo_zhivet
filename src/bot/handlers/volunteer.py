from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.bot.handlers.start import start
from src.bot.handlers.state_constants import (
    ACTIVITY_RADIUS,
    ADDING_VOLUNTEER,
    ADDRESS,
    ADDRESS_INPUT,
    ADDRESS_TEMPORARY,
    BACK,
    CAR_COMMAND,
    CHECK_MARK,
    CURRENT_FEATURE,
    EDIT_PROFILE_GREETING,
    END,
    FEATURES,
    FEATURES_DESCRIPTION,
    IS_EXISTS,
    PHONE_COMMAND,
    PHONE_INPUT,
    RADIUS_COMMAND,
    REGISTER_GREETING,
    SAVE,
    SECOND_LEVEL_TEXT,
    SECOND_LEVEL_UPDATE_TEXT,
    SELECTING_OVER,
    SPECIFY_ACTIVITY_RADIUS,
    SPECIFY_CAR_AVAILABILITY,
    SPECIFY_PHONE_PERMISSION,
    START_OVER,
    TELEGRAM_ID,
    TELEGRAM_USERNAME,
    VALIDATE,
)
from src.bot.service.get_issues_with_statuses import processing_volunteer
from src.bot.service.phone_number import format_numbers, phone_number_validate
from src.bot.service.save_new_user import create_new_user
from src.bot.service.save_tracker_id import save_tracker_id
from src.bot.service.volunteer import (
    check_and_update_volunteer,
    create_volunteer,
    create_volunteer_ticket,
    update_volunteer_ticket,
    volunteer_data_preparation,
)
from src.core.db.db import get_async_session
from src.core.db.repository.user_repository import crud_user
from src.core.db.repository.volunteer_repository import crud_volunteer


def get_buttons_params(is_volunteer_exists: bool) -> tuple[str, str, str, str]:
    """Формирует параметры кнопок регистрации/редактирования волонтера"""
    if is_volunteer_exists:
        action = "Редактировать"
        save_action = "Сохранить"
        text = EDIT_PROFILE_GREETING + FEATURES_DESCRIPTION
        second_level_text = SECOND_LEVEL_UPDATE_TEXT
    else:
        action = "Указать"
        save_action = "Отправить заявку"
        text = REGISTER_GREETING + FEATURES_DESCRIPTION
        second_level_text = SECOND_LEVEL_TEXT
    return action, save_action, text, second_level_text


async def add_volunteer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Меню регистрации волонтёра."""

    if context.user_data.get(IS_EXISTS) is None:
        session_generator = get_async_session()
        session = await session_generator.asend(None)
        context.user_data[IS_EXISTS] = await crud_volunteer.get_exist_by_attribute(
            TELEGRAM_ID, update.effective_chat.id, session
        )
        context.chat_data["current_session"] = session
    action, save_action, text, second_level_text = get_buttons_params(context.user_data[IS_EXISTS])

    def check_feature(feature):
        return FEATURES in context.user_data and feature in context.user_data[FEATURES]

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{action} свой адрес {CHECK_MARK*check_feature(ADDRESS)}", callback_data=ADDRESS_INPUT
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"{action} радиус активности {CHECK_MARK*check_feature(SPECIFY_ACTIVITY_RADIUS)}",
                callback_data=SPECIFY_ACTIVITY_RADIUS,
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"{action} наличие автомобиля {CHECK_MARK*check_feature(SPECIFY_CAR_AVAILABILITY)}",
                callback_data=SPECIFY_CAR_AVAILABILITY,
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"{action} номер телефона {CHECK_MARK*check_feature(SPECIFY_PHONE_PERMISSION)}",
                callback_data=SPECIFY_PHONE_PERMISSION,
            ),
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
    elif FEATURES not in context.user_data:
        # context.user_data[START_OVER] = False
        return await start(update, context)

    else:
        if check_data(context.user_data[FEATURES]) or context.user_data[IS_EXISTS]:
            buttons.append([InlineKeyboardButton(text=f"{save_action}", callback_data=SAVE)])
            keyboard = InlineKeyboardMarkup(buttons)
        if update.message is not None:
            await update.message.reply_text(text=second_level_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        else:
            await update.callback_query.edit_message_text(
                text=second_level_text, reply_markup=keyboard, parse_mode=ParseMode.HTML
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
    text = 'Укажите свой номер телефона начиная с "8" или "+7":'
    button = [[InlineKeyboardButton(text="Назад", callback_data=BACK)]]
    keyboard = InlineKeyboardMarkup(button)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return VALIDATE


async def handle_phone_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_input = update.message.text
    phone = phone_number_validate(user_input)
    if phone is None:
        chat_text = "Пожалуйста, введите корректный номер телефона."

        buttons = [
            [
                InlineKeyboardButton(text="Указать телефон заново", callback_data=PHONE_INPUT),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data=BACK),
            ],
        ]

        keyboard = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(text=chat_text, reply_markup=keyboard)
    else:
        text = f"Проверьте введённый номер:\n{format_numbers(phone)}"
        context.user_data[CURRENT_FEATURE] = SPECIFY_PHONE_PERMISSION

        data = PHONE_COMMAND + phone
        buttons = [
            [
                InlineKeyboardButton(text="Верно", callback_data=data),
            ],
            [
                InlineKeyboardButton(text="Указать телефон заново", callback_data=PHONE_INPUT),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data=BACK),
            ],
        ]

        keyboard = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(text=text, reply_markup=keyboard)

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
            InlineKeyboardButton(text="Да", callback_data=CAR_COMMAND + "Да"),
            InlineKeyboardButton(text="Нет", callback_data=CAR_COMMAND + "Нет"),
        ],
        [InlineKeyboardButton(text="Назад", callback_data=BACK)],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_OVER


async def save_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Сохранение данных в контексте."""

    current_feature_value = update.callback_query.data

    user_data = context.user_data
    user_data[FEATURES] |= context.user_data.pop(ADDRESS_TEMPORARY, {})

    user_data[FEATURES][user_data[CURRENT_FEATURE]] = current_feature_value

    user_data[START_OVER] = True

    return await add_volunteer(update, context)


async def save_and_exit_volunteer(
    telegram_id: int,
    username: str,
    first_name: str,
    last_name: str,
    volunteer_data,
    volunteer_is_exists: bool,
) -> None:
    """Сохранение данных в базу и отправка в трекер"""
    session_generator = get_async_session()
    session = await session_generator.asend(None)

    old_user = await crud_user.get_user_by_telegram_id(telegram_id, session)
    if old_user and old_user.is_banned:
        return
    if old_user is None:
        await create_new_user({TELEGRAM_ID: telegram_id, TELEGRAM_USERNAME: username}, session)

    volunteer_data = volunteer_data_preparation(telegram_id, username, first_name, last_name, volunteer_data)

    if volunteer_is_exists:
        volunteer, old_ticket_id = await check_and_update_volunteer(volunteer_data, session)
        if volunteer is None:
            return
        update_volunteer_ticket(volunteer, old_ticket_id)
    else:
        volunteer = await create_volunteer(volunteer_data, session)
        tracker = create_volunteer_ticket(volunteer)
        await save_tracker_id(crud_volunteer, tracker.key, volunteer.telegram_id, session)
        await processing_volunteer(volunteer, session)


async def back_to_add_volunteer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data[START_OVER] = True
    context.user_data.pop(ADDRESS_TEMPORARY, None)

    return await add_volunteer(update, context)


def check_data(user_data) -> bool:
    return all((feature in user_data for feature in (ADDRESS, SPECIFY_ACTIVITY_RADIUS, SPECIFY_CAR_AVAILABILITY)))
