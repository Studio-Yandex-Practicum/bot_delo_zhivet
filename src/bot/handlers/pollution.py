from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from api.tracker import client
from .start import start
from .state_constants import (CURRENT_FEATURE, END, FEATURES,
                              POLLUTION_COMMENT, POLLUTION_COORDINATES,
                              POLLUTION_FOTO, SAVE, SELECTING_FEATURE,
                              START_OVER, TYPING, FILE_PATH, POLLUTION,
                              LATITUDE, LONGITUDE)


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
    await photo_file.download_to_drive("user_photo.jpg")
    user_data[FEATURES][user_data[CURRENT_FEATURE]] = photo_file
    user_data[START_OVER] = True

    return await select_option_to_report_about_pollution(update, context)


async def save_location(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """Сохранение локации"""
    user_data = context.user_data
    user_data[FEATURES][user_data[CURRENT_FEATURE]] = update.message.location
    user_data[START_OVER] = True

    return await select_option_to_report_about_pollution(update, context)


async def save_and_exit_pollution(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """Сохранение данных в базу"""
    context.user_data[START_OVER] = True
    user_data = context.user_data[FEATURES]
    file_path = user_data[POLLUTION_FOTO][FILE_PATH]
    latitude = user_data[POLLUTION_COORDINATES][LATITUDE]
    longitude = user_data[POLLUTION_COORDINATES][LONGITUDE]
    if POLLUTION_COMMENT in user_data:
        comment = user_data[POLLUTION_COMMENT]
    else:
        comment = "Комментариев не оставили"
    summary = f"{latitude}, {longitude}"
    description = f"""
    Координаты: {latitude}, {longitude}
    Комментарий: {comment}
    {file_path}
    """
    client.issues.create(
        queue=POLLUTION, summary=summary, description=description,
    )

    await start(update, context)
    return END


def check_data(user_data):
    if POLLUTION_COORDINATES in user_data and POLLUTION_FOTO in user_data:
        return True
    else:
        return False
