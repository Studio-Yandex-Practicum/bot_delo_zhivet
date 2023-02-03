from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.api.tracker import client
from src.bot.service.pollution import create_new_pollution
from src.bot.service.save_new_user import create_new_user
from src.bot.service.save_tracker_id import save_tracker_id_pollution
from src.core.db.db import get_async_session

from .start import start
from .state_constants import (CURRENT_FEATURE, END, FEATURES, LATITUDE,
                              LONGITUDE, POLLUTION, POLLUTION_COMMENT,
                              POLLUTION_COORDINATES, POLLUTION_FOTO, SAVE,
                              SELECTING_FEATURE, START_OVER, TELEGRAM_ID,
                              TYPING)


async def select_option_to_report_about_pollution(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    text = "Заполните данные о загрязнении"
    buttons = [
        [
            InlineKeyboardButton(
                text="Загрузите фото",
                callback_data=POLLUTION_FOTO
            ),
            InlineKeyboardButton(
                text="Добавьте координаты",
                callback_data=POLLUTION_COORDINATES
            ),
        ],
        [
            InlineKeyboardButton(
                text="Напишите комментарий",
                callback_data=POLLUTION_COMMENT
            ),
            InlineKeyboardButton(
                text="Выйти", callback_data=str(END)
            ),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    if not context.user_data.get(START_OVER):
        context.user_data[FEATURES] = {}
        text = "Пожалуйста, выберите функцию для добавления."
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=text, reply_markup=keyboard
        )
    else:
        if check_data(context.user_data[FEATURES]) is True:
            buttons.append(
                [InlineKeyboardButton(
                    text="Сохранить и выйти", callback_data=SAVE
                )]
            )
            keyboard = InlineKeyboardMarkup(buttons)

        text = "Готово! Пожалуйста, выберите функцию для добавления."
        if update.message is not None:
            await update.message.reply_text(text=text, reply_markup=keyboard)
        else:
            await update.callback_query.edit_message_caption(
                text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_FEATURE


async def end_second_level(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Возврат к верхнему диалогу"""
    context.user_data[START_OVER] = True
    await start(update, context)

    return END


async def input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Добавление информации"""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = "Отлично, что ты хочешь добавить?"
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)

    return TYPING


async def save_comment(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """Сохранение комментария"""
    user_data = context.user_data
    user_data[FEATURES][user_data[CURRENT_FEATURE]] = update.message.text
    user_data[START_OVER] = True

    return await select_option_to_report_about_pollution(update, context)


async def save_foto(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """Сохранение фотографии"""
    user_data = context.user_data
    photo_file = await update.message.photo[-1].get_file()
    date = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    file_path = f"media\\{date}.jpg"
    await photo_file.download_to_drive(custom_path=file_path)
    user_data[FEATURES][user_data[CURRENT_FEATURE]] = str(file_path)
    user_data[START_OVER] = True

    return await select_option_to_report_about_pollution(update, context)


async def save_location(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """Сохранение локации"""
    user_data = context.user_data
    user_data[FEATURES][LONGITUDE] = update.message.location.longitude
    user_data[FEATURES][LATITUDE] = update.message.location.latitude
    user_data[START_OVER] = True

    return await select_option_to_report_about_pollution(update, context)


async def save_and_exit_pollution(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """Сохранение данных в базу"""
    context.user_data[START_OVER] = True
    user_data = context.user_data[FEATURES]
    user_data[TELEGRAM_ID] = update.effective_user.id
    file_path = user_data[POLLUTION_FOTO]
    latitude = user_data[LATITUDE]
    longitude = user_data[LONGITUDE]
    if POLLUTION_COMMENT in user_data:
        comment = user_data[POLLUTION_COMMENT]
    else:
        comment = "Комментариев не оставили"
    session_generator = get_async_session()
    session = await session_generator.asend(None)
    await create_new_user(user_data[TELEGRAM_ID], session)
    await create_new_pollution(user_data, session)
    summary = f"{latitude}, {longitude}"
    description = f"""
    Координаты: {latitude}, {longitude}
    Комментарий: {comment}
    """
    client.issues.create(
        queue=POLLUTION, summary=summary, description=description,
    )
    await save_tracker_id_pollution(summary, user_data[TELEGRAM_ID], file_path, session)
    await start(update, context)
    return END


def check_data(user_data):
    if LATITUDE in user_data and POLLUTION_FOTO in user_data:
        return True
    else:
        return False
