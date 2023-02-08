from html import escape
from uuid import uuid4

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
)
from telegram.constants import MessageEntityType, ParseMode
from telegram.ext import ContextTypes

from src.bot.handlers.start import start
from src.bot.handlers.state_constants import CURRENT_LEVEL, END, FEATURES, MAKING_DONATION, START_OVER, TELEGRAM_ID
from src.bot.service.save_new_user import create_new_user
from src.core.db.db import get_async_session


async def become_volunteer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # noqa
    await update.message.reply_text('Раздел "Стать волонтёром"')


async def make_donation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    session_generator = get_async_session()
    session = await session_generator.asend(None)
    await create_new_user(telegram_id, session)
    text = "Стать жервтой нажми на кнопку"
    level = update.callback_query.data
    context.user_data[CURRENT_LEVEL] = level
    buttons = [
        [
            InlineKeyboardButton(
                text="Сайт с пожертвованием", url="https://delozhivet.ru/campaign/pomoch-delo-zhivet/"
            ),
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return MAKING_DONATION


async def end_second_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Возврат к главному меню."""
    context.user_data[START_OVER] = True
    await start(update, context)

    return END

    # await update.message.reply_text("https://delozhivet.ru/campaign/pomoch-delo-zhivet/")


"""
async def make_donation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query
    if query == "":

        return
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Caps",
            input_message_content=InputTextMessageContent(f"ПРИВЕТ<b>{escape(query)}</b>", parse_mode=ParseMode.HTML),
        ),
    ]
    await update.inline_query.answer(results)
"""
