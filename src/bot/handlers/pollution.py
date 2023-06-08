import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.api.tracker import client
from src.bot.const import KB_IN_MB, MAXIMUM_SIZE_OF_IMAGE_KB
from src.bot.handlers.start import start
from src.bot.handlers.state_constants import (
    ADD_POLLUTION_TAG, BACK, CHECK_MARK, CURRENT_FEATURE, END, FEATURES,
    LATITUDE, LONGITUDE, POLLUTION_COMMENT, POLLUTION_COORDINATES,
    POLLUTION_FOTO, POLLUTION_TAGS, SAVE, SECOND_LEVEL_TEXT, SELECTING_FEATURE,
    START_OVER, TYPING,
)
from src.bot.service.pollution import (
    create_new_pollution, create_new_pollution_dict_from_data,
    create_new_pollution_message_for_tracker, download_to_object_storage,
    resize_downloaded_image,
)
from src.bot.service.save_new_user import get_or_create_user
from src.bot.service.save_tracker_id import other_save_tracker_id
from src.bot.service.tags import check_pollution_tags_are_in_db
from src.bot.service.volunteer import volunteers_description
from src.core.db.db import get_async_session
from src.core.db.model import Pollution, User, Volunteer
from src.core.db.repository.pollution_repository import crud_pollution
from src.core.db.repository.volunteer_repository import crud_volunteer


async def select_option_to_report_about_pollution(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    def check_feature(feature):
        return FEATURES in context.user_data and feature in context.user_data[FEATURES]

    buttons = [
        [
            InlineKeyboardButton(
                text=f"Загрузить фото {CHECK_MARK*check_feature(POLLUTION_FOTO)}", callback_data=POLLUTION_FOTO
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"Отправить координаты {CHECK_MARK*check_feature(LATITUDE)}",
                callback_data=POLLUTION_COORDINATES,
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"Оставить комментарий {CHECK_MARK*check_feature(POLLUTION_COMMENT)}",
                callback_data=POLLUTION_COMMENT,
            ),
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=str(END)),
        ],
    ]

    session_generator = get_async_session()
    session = await session_generator.asend(None)
    tag = await check_pollution_tags_are_in_db(session)
    if tag:
        buttons.insert(
            3,
            [
                InlineKeyboardButton(
                    text=f"Указать тип проблемы {CHECK_MARK*check_feature(POLLUTION_TAGS)}",
                    callback_data=ADD_POLLUTION_TAG,
                ),
            ],
        )

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


async def end_second_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Возврат к верхнему диалогу"""
    context.user_data[START_OVER] = True
    await start(update, context)

    return END


async def input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление информации"""
    if POLLUTION_FOTO == update.callback_query.data:
        text = "Загрузите фотографию"
        context.user_data[CURRENT_FEATURE] = update.callback_query.data
    elif POLLUTION_COMMENT == update.callback_query.data:
        text = "Напишите, если что-то важно знать об обнаруженной проблеме:"
        context.user_data[CURRENT_FEATURE] = update.callback_query.data
    elif POLLUTION_COORDINATES == update.callback_query.data:
        context.user_data[CURRENT_FEATURE] = update.callback_query.data
        text = (
            "Отправьте геопозицию, для этого:\n"
            "1. Нажмите на значок в виде «скрепки», находится справа от поля ввода;\n"
            "2. В открывшемся меню выберите «Геопозиция»;\n"
            "3. Выберете место на карте и нажмите «Отправить геопозицию»."
        )
    button = [[InlineKeyboardButton(text="Назад", callback_data=BACK)]]
    keyboard = InlineKeyboardMarkup(button)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return TYPING


async def save_comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Сохранение комментария"""
    user_data = context.user_data
    if context.user_data[CURRENT_FEATURE] == POLLUTION_COMMENT:
        user_data[FEATURES][POLLUTION_COMMENT] = update.message.text
        user_data[START_OVER] = True

        return await select_option_to_report_about_pollution(update, context)
    else:
        chat_text = "Вы ввели некорректные данные, возможно вы хотели добавить комментарий?"
        buttons = [
            [
                InlineKeyboardButton(text="Перейти к добавлению комментария", callback_data=POLLUTION_COMMENT),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data=BACK),
            ],
        ]

        keyboard = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(text=chat_text, reply_markup=keyboard)


async def save_foto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Сохранение фотографии"""
    user_data = context.user_data
    if context.user_data[CURRENT_FEATURE] == POLLUTION_FOTO:
        if update.message.photo:
            photo_file = await update.message.effective_attachment[-1].get_file()
        elif update.message.document.mime_type == "image/jpeg":
            photo_file = await update.message.effective_attachment.get_file()
        elif update.message.document.mime_type == "image/png":
            photo_file = await update.message.effective_attachment.get_file()
        else:
            chat_text = "Вы ввели некорректные данные, возможно вы хотели добавить фотографию?"
            buttons = [
                [
                    InlineKeyboardButton(text="Перейти к добавлению фотографии", callback_data=POLLUTION_FOTO),
                ],
                [
                    InlineKeyboardButton(text="Назад", callback_data=BACK),
                ],
            ]
            keyboard = InlineKeyboardMarkup(buttons)
            await update.message.reply_text(text=chat_text, reply_markup=keyboard)

        date = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        unique_uuid_name = str(uuid4())
        file_path = Path.cwd() / "media" / f"{date}_{unique_uuid_name}.jpg"
        await photo_file.download_to_drive(custom_path=file_path)
        user_data[FEATURES][POLLUTION_FOTO] = str(file_path)
        user_data[START_OVER] = True

        size_of_photo_in_kbytes = int(os.stat(file_path).st_size // KB_IN_MB)
        if size_of_photo_in_kbytes > MAXIMUM_SIZE_OF_IMAGE_KB:
            await resize_downloaded_image(file_path)

        return await select_option_to_report_about_pollution(update, context)


async def save_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Сохранение локации"""
    user_data = context.user_data
    if context.user_data[CURRENT_FEATURE] == POLLUTION_COORDINATES:
        user_data[FEATURES][LONGITUDE] = update.message.location.longitude
        user_data[FEATURES][LATITUDE] = update.message.location.latitude
        user_data[START_OVER] = True

        return await select_option_to_report_about_pollution(update, context)
    else:
        chat_text = "Вы ввели некорректные данные, возможно вы хотели добавить коррдинаты?"
        buttons = [
            [
                InlineKeyboardButton(text="Перейти к добавлению координат", callback_data=POLLUTION_COORDINATES),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data=BACK),
            ],
        ]

        keyboard = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(text=chat_text, reply_markup=keyboard)


async def save_and_exit_pollution(
    user_id: int,
    username: str,
    user_data,
) -> None:
    """Сохранение данных в базу и отправка в трекер"""

    session_generator = get_async_session()
    session = await session_generator.asend(None)

    user_db: User = await get_or_create_user(user_id, username, session)
    if user_db.is_banned:
        return

    file_path: str = user_data[POLLUTION_FOTO]
    await download_to_object_storage(file_path)

    new_pollution_data: dict = await create_new_pollution_dict_from_data(user_db.telegram_id, user_data, session)
    new_pollution_db: Pollution = await create_new_pollution(new_pollution_data, session)
    volunteers: list[Volunteer] = await crud_volunteer.get_volunteers_by_point(
        new_pollution_db.longitude, new_pollution_db.latitude, session
    )
    message: dict = create_new_pollution_message_for_tracker(new_pollution_db, volunteers_description(volunteers))
    tracker = client.issues.create(**message)
    await other_save_tracker_id(crud_pollution, tracker.key, new_pollution_db, session)
    os.remove(file_path)


async def back_to_select_option_to_report_about_pollution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data[START_OVER] = True

    return await select_option_to_report_about_pollution(update, context)


def check_data(user_data):
    if LATITUDE in user_data and POLLUTION_FOTO in user_data:
        return True
    else:
        return False
