from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from api.tracker import client
from bot.handlers.state_constants import (
    ADD_SOCIAL_TAG,
    ADDRESS_TEMPORARY,
    BACK,
    CHECK_MARK,
    CITY,
    CITY_INPUT,
    CITY_SOCIAL,
    CURRENT_FEATURE,
    END,
    FEATURES,
    SAVE,
    SECOND_LEVEL_TEXT,
    SELECTING_FEATURE,
    SOCIAL_ADDRESS,
    SOCIAL_COMMENT,
    SOCIAL_PROBLEM_ADDRESS,
    SOCIAL_PROBLEM_TYPING,
    SOCIAL_TAGS,
    START_OVER,
    TYPING_SOCIAL_CITY,
)
from bot.service.dadata import get_fields_from_dadata
from src.bot.service.assistance_disabled import (
    create_new_social,
    create_new_social_dict_from_data,
    create_new_social_message_for_tracker,
)
from src.bot.service.save_new_user import get_or_create_user
from src.bot.service.save_tracker_id import other_save_tracker_id
from src.bot.service.tags import check_assistance_tags_are_in_db
from src.bot.service.volunteer import volunteers_description
from src.core.db.db import get_async_session
from src.core.db.model import Assistance_disabled
from src.core.db.repository.assistance_disabled_repository import crud_assistance_disabled
from src.core.db.repository.volunteer_repository import crud_volunteer


async def input_social_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление информации"""

    # TODO: Если вбиваем адрес, нужна проверка корректности(или отдельная функция инпута адреса с проверкой)

    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = "Укажите контакты адресата помощи для связи и уточните, с чем нужна помощь:"
    button = [[InlineKeyboardButton(text="Назад", callback_data=BACK)]]
    keyboard = InlineKeyboardMarkup(button)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SOCIAL_PROBLEM_TYPING


async def ask_for_input_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Предложить пользователю ввести данные о населенном пункте."""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = "Укажите адрес, по которому нужно оказать помощь:"
    button = [[InlineKeyboardButton(text="Назад", callback_data=BACK)]]
    keyboard = InlineKeyboardMarkup(button)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return TYPING_SOCIAL_CITY


async def address_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Обработчик данных о населенном пункте с выводом возможных вариантов."""
    user_input = update.message.text
    address = get_fields_from_dadata(user_input)
    if address is not None:
        text = (
            f"Это правильный адрес: {address['full_address']}? "
            'Если адрес не правильный, то выберите "Нет" и укажите более подробный вариант адреса, '
            "а мы постараемся определить его правильно!"
        )
        context.user_data[ADDRESS_TEMPORARY] = address

        buttons = [
            [
                InlineKeyboardButton(text="Да", callback_data=CITY_SOCIAL),
                InlineKeyboardButton(text="Нет", callback_data=CITY_INPUT),
            ],
            [InlineKeyboardButton(text="Назад", callback_data=BACK)],
        ]

        keyboard = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(text=text, reply_markup=keyboard)

    else:
        chat_text = "Не нашли такой адрес. Пожалуйста, укажи адрес подробнее:"
        buttons = [
            [
                InlineKeyboardButton(text="Указать адрес заново", callback_data=CITY_INPUT),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data=BACK),
            ],
        ]

        keyboard = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(text=chat_text, reply_markup=keyboard)

    return SOCIAL_PROBLEM_ADDRESS


async def save_social_problem_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data[FEATURES][user_data[CURRENT_FEATURE]] = update.message.text
    user_data[START_OVER] = True

    return await report_about_social_problem(update, context)


async def save_social_address_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение данных в контексте."""

    city = update.callback_query.data

    user_data = context.user_data
    user_data[FEATURES] |= context.user_data.pop(ADDRESS_TEMPORARY, {})
    user_data[FEATURES][user_data[CURRENT_FEATURE]] = city

    user_data[START_OVER] = True

    return await report_about_social_problem(update, context)


async def report_about_social_problem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    def check_feature(feature):
        return FEATURES in context.user_data and feature in context.user_data[FEATURES]

    text = "Заполните данные об обращении"
    buttons = [
        [
            InlineKeyboardButton(text=f"Указать адрес {CHECK_MARK*check_feature(CITY)}", callback_data=SOCIAL_ADDRESS),
        ],
        [
            InlineKeyboardButton(
                text=f"Оставить контакты и комментарий {CHECK_MARK*check_feature(SOCIAL_COMMENT)}",
                callback_data=SOCIAL_COMMENT,
            )
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=str(END)),
        ],
    ]

    session_generator = get_async_session()
    session = await session_generator.asend(None)
    tag = await check_assistance_tags_are_in_db(session)
    if tag:
        buttons.insert(
            2,
            [
                InlineKeyboardButton(
                    text=f"Указать тип проблемы {CHECK_MARK*check_feature(SOCIAL_TAGS)}",
                    callback_data=ADD_SOCIAL_TAG,
                ),
            ],
        )

    keyboard = InlineKeyboardMarkup(buttons)

    if not context.user_data.get(START_OVER):
        context.user_data[FEATURES] = {}
        text = (
            "Пожалуйста, укажите адрес, по которому нужна помощь, и оставьте контакты и комментарий – это "
            "обязательно нужно для того, чтобы мы взяли заявку в работу:"
        )
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
    return SELECTING_FEATURE


async def save_and_exit_from_social_problem(
    user_id: int,
    username: str,
    user_data,
) -> None:
    """Сохранение данных в базу и отправка в трекер"""

    session_generator = get_async_session()
    session = await session_generator.asend(None)

    user_db = await get_or_create_user(user_id, username, session)
    if user_db.is_banned:
        return

    new_social_data: dict = await create_new_social_dict_from_data(user_db.telegram_id, user_data, session)
    new_social_db: Assistance_disabled = await create_new_social(new_social_data, session)
    volunteers = await crud_volunteer.get_volunteers_by_point(new_social_db.longitude, new_social_db.latitude, session)
    message: dict = create_new_social_message_for_tracker(new_social_db, volunteers_description(volunteers))
    tracker = client.issues.create(**message)
    await other_save_tracker_id(crud_assistance_disabled, tracker.key, new_social_db, session)


async def back_to_add_social(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data[START_OVER] = True
    context.user_data.pop(ADDRESS_TEMPORARY, None)

    return await report_about_social_problem(update, context)


def check_data(user_data):
    if CITY in user_data and SOCIAL_COMMENT in user_data:
        return True
    else:
        return False
