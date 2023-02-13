from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from api.tracker import client
from bot.handlers.start import start
from bot.handlers.state_constants import (
    BACK,
    CITY_INPUT,
    CITY_SOCIAL,
    CURRENT_FEATURE,
    END,
    FEATURES,
    SAVE,
    SELECTING_FEATURE,
    SOCIAL,
    SOCIAL_ADDRESS,
    SOCIAL_COMMENT,
    SOCIAL_PROBLEM_ADDRESS,
    SOCIAL_PROBLEM_TYPING,
    START_OVER,
    TELEGRAM_ID,
    TELEGRAM_USERNAME,
    TYPING_SOCIAL_CITY,
)
from bot.service.dadata import get_fields_from_dadata
from src.bot.service.assistance_disabled import create_new_social
from src.bot.service.save_new_user import create_new_user
from src.bot.service.save_tracker_id import save_tracker_id_assistance_disabled
from src.core.db.db import get_async_session
from src.core.db.repository.assistance_disabled_repository import crud_assistance_disabled

load_dotenv(".env")


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
        context.user_data[FEATURES] = address

        data = CITY_SOCIAL + user_input
        buttons = [
            [
                InlineKeyboardButton(text="Да", callback_data=data),
                InlineKeyboardButton(text="Нет", callback_data=CITY_INPUT),
            ]
        ]

        keyboard = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(text=text, reply_markup=keyboard)

        return SOCIAL_PROBLEM_ADDRESS
    else:
        chat_text = "Не нашли такой адрес. Пожалуйста, укажи адрес подробнее:"
        context.user_data[FEATURES] = address

        data = CITY_SOCIAL + user_input
        buttons = [
            [
                InlineKeyboardButton(text="Указать адрес заново", callback_data=CITY_INPUT),
            ]
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
    user_data[FEATURES][user_data[CURRENT_FEATURE]] = city

    user_data[START_OVER] = True

    return await report_about_social_problem(update, context)


async def report_about_social_problem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    text = "Заполните данные об обращении"
    buttons = [
        [
            InlineKeyboardButton(text="Указать адрес", callback_data=SOCIAL_ADDRESS),
        ],
        [InlineKeyboardButton(text="Оставить контакты и комментарий", callback_data=SOCIAL_COMMENT)],
        [
            InlineKeyboardButton(text="Назад", callback_data=str(END)),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    if not context.user_data.get(START_OVER):
        context.user_data[FEATURES] = {}
        text = (
            "Пожалуйста, укажите адрес, по которому нужна помощь и оставьте контакты и комментарий – это "
            "обязательно нужно для того, чтобы мы взяли заявку в работу:"
        )
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        if check_data(context.user_data[FEATURES]) is True:
            buttons.append([InlineKeyboardButton(text="Отправить заявку на помощь", callback_data=SAVE)])
            keyboard = InlineKeyboardMarkup(buttons)

        text = "Готово! Пожалуйста, выберите функцию для добавления."
        if update.message is not None:
            await update.message.reply_text(text=text, reply_markup=keyboard)
        else:
            await update.callback_query.edit_message_text(text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_FEATURE


async def save_and_exit_from_social_problem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохранение данных в базу и отправка в трекер"""
    context.user_data[START_OVER] = True
    user_data = context.user_data[FEATURES]
    user_data[TELEGRAM_ID] = update.effective_user.id
    del user_data[SOCIAL_ADDRESS]
    user = {}
    user[TELEGRAM_ID] = user_data[TELEGRAM_ID]
    user[TELEGRAM_USERNAME] = update.effective_user.username
    session_generator = get_async_session()
    session = await session_generator.asend(None)
    await create_new_user(user, session)
    await create_new_social(user_data, session)
    city = await crud_assistance_disabled.get_full_address_by_telegram_id(user_data[TELEGRAM_ID], session)
    description = f"""
    Ник в телеграмме оставившего заявку: {user[TELEGRAM_USERNAME]}
    Комментарий к заявке: {user_data[SOCIAL_COMMENT]}
    """
    client.issues.create(
        queue=SOCIAL,
        summary=city,
        description=description,
    )
    await save_tracker_id_assistance_disabled(city, user_data[TELEGRAM_ID], session)
    await start(update, context)
    return END


def check_data(user_data):
    if SOCIAL_ADDRESS in user_data and SOCIAL_COMMENT in user_data:
        return True
    else:
        return False
