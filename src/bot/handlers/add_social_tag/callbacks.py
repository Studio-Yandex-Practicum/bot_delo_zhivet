from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.handlers.state_constants import (
    ADD_SOCIAL_TAG, BACK, CURRENT_FEATURE, FEATURES, NO_TAG, SAVE_TAG, TAG_ID,
)
from src.bot.handlers.social import back_to_add_social
from src.bot.service.tags import (
    check_social_tag_exists, get_all_assistance_tags,
)


async def input_social_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор тега из списка тегов"""
    buttons = []
    text = "Выберите один, наиболее подходящий тег:"
    tags = await get_all_assistance_tags()
    for tag in tags:
        # на кнопке написано имя тега, нажатие на кнопку отправит боту tag.id
        buttons.append([InlineKeyboardButton(text=str(tag.name), callback_data=str(tag.id))])
    buttons.append([InlineKeyboardButton(text="Без тега", callback_data=NO_TAG)])
    buttons.append([InlineKeyboardButton(text="Назад", callback_data=BACK)])
    keyboard = InlineKeyboardMarkup(buttons)
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return SAVE_TAG


async def save_social_tag_to_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение тега."""
    if context.user_data[CURRENT_FEATURE] == ADD_SOCIAL_TAG:
        if update.callback_query.data == NO_TAG:
            context.user_data[FEATURES].pop(TAG_ID, None)
            return await back_to_add_social(update, context)
        if update.callback_query.data == BACK:
            return await back_to_add_social(update, context)
        if await check_social_tag_exists(update.callback_query.data):
            context.user_data[FEATURES][TAG_ID] = update.callback_query.data
            return await back_to_add_social(update, context)
    chat_text = "Вы ввели некорректные данные, возможно вы хотели добавить тег?"
    buttons = [
        [
            InlineKeyboardButton(text="Перейти к добавлению тега", callback_data=ADD_SOCIAL_TAG),
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=BACK),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)
    await update.callback_query.edit_message_text(text=chat_text, reply_markup=keyboard)
