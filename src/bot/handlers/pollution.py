from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.api.tracker import client
from src.bot.service.pollution import create_new_pollution
from src.bot.service.save_new_user import create_new_user
from src.bot.service.save_tracker_id import save_tracker_id_pollution
from src.core.db.db import get_async_session

from .start import start
from .state_constants import (
    BACK,
    END,
    FEATURES,
    GEOM,
    LATITUDE,
    LONGITUDE,
    POLLUTION,
    POLLUTION_COMMENT,
    POLLUTION_COORDINATES,
    POLLUTION_FOTO,
    SAVE,
    SELECTING_FEATURE,
    START_OVER,
    TELEGRAM_ID,
    TELEGRAM_USERNAME,
    TYPING,
)


async def select_option_to_report_about_pollution(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    text = "Заполните данные о загрязнении"
    buttons = [
        [
            InlineKeyboardButton(text="Загрузите фото", callback_data=POLLUTION_FOTO),
            InlineKeyboardButton(text="Отправить координаты", callback_data=POLLUTION_COORDINATES),
        ],
        [
            InlineKeyboardButton(text="Написать комментарий", callback_data=POLLUTION_COMMENT),
            InlineKeyboardButton(text="Выйти", callback_data=str(END)),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    if not context.user_data.get(START_OVER):
        context.user_data[FEATURES] = {}
        text = (
            "Пожалуйста, добавьте фотографию и отправьте геометку места, где обнаружена проблема – это обязательно "
            "нужно для того, чтобы мы взяли заявку в работу. Если что-то нужно добавить, оставьте комментарий:"
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
            await update.callback_query.edit_message_caption(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_FEATURE


async def end_second_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Возврат к верхнему диалогу"""
    context.user_data[START_OVER] = True
    await start(update, context)

    return END


async def input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление информации"""
    if POLLUTION_FOTO == update.callback_query.data:
        text = "Загрузите фотографию"
    elif POLLUTION_COMMENT == update.callback_query.data:
        text = "Напишите, если что-то важно знать об обнаруженной проблеме:"
    elif POLLUTION_COORDINATES == update.callback_query.data:
        text = "Отправьте геометку"
    button = [[InlineKeyboardButton(text="Назад", callback_data=BACK)]]
    keyboard = InlineKeyboardMarkup(button)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return TYPING


async def save_comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Сохранение комментария"""
    user_data = context.user_data
    user_data[FEATURES][POLLUTION_COMMENT] = update.message.text
    user_data[START_OVER] = True

    return await select_option_to_report_about_pollution(update, context)


async def save_foto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Сохранение фотографии"""
    user_data = context.user_data
    photo_file = await update.message.photo[-1].get_file()
    date = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    file_path = f"media\\{date}.jpg"
    await photo_file.download_to_drive(custom_path=file_path)
    user_data[FEATURES][POLLUTION_FOTO] = str(file_path)
    user_data[START_OVER] = True

    return await select_option_to_report_about_pollution(update, context)


async def save_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Сохранение локации"""
    user_data = context.user_data
    user_data[FEATURES][LONGITUDE] = update.message.location.longitude
    user_data[FEATURES][LATITUDE] = update.message.location.latitude
    user_data[START_OVER] = True

    return await select_option_to_report_about_pollution(update, context)


async def save_and_exit_pollution(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Сохранение данных в базу"""
    context.user_data[START_OVER] = True
    user_data = context.user_data[FEATURES]
    user_data[TELEGRAM_ID] = update.effective_user.id
    user_data[GEOM] = f"POINT({user_data[LATITUDE]} {user_data[LONGITUDE]})"
    file_path = user_data[POLLUTION_FOTO]
    latitude = user_data[LATITUDE]
    longitude = user_data[LONGITUDE]
    if POLLUTION_COMMENT in user_data:
        comment = user_data[POLLUTION_COMMENT]
    else:
        comment = "Комментариев не оставили"
    user = {}
    user[TELEGRAM_ID] = user_data[TELEGRAM_ID]
    user[TELEGRAM_USERNAME] = update.effective_user.username
    session_generator = get_async_session()
    session = await session_generator.asend(None)
    await create_new_user(user, session)
    await create_new_pollution(user_data, session)
    summary = f"{user[TELEGRAM_USERNAME]} - {latitude}, {longitude}"
    description = f"""
    Ник в телеграмме оставившего заявку: {user[TELEGRAM_USERNAME]}
    Координаты загрязнения: {latitude}, {longitude}
    Комментарий к заявке: {comment}
    """
    client.issues.create(
        queue=POLLUTION,
        summary=summary,
        description=description,
    )
    await save_tracker_id_pollution(summary, user_data[TELEGRAM_ID], file_path, session)
    await start(update, context)
    return END


def check_data(user_data):
    if LATITUDE in user_data and POLLUTION_FOTO in user_data:
        return True
    else:
        return False
