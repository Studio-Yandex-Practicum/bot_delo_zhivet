from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.start import start
from bot.handlers.state_constants import CURRENT_LEVEL, END, FEATURES, START_OVER, STOPPING


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка окончания разговора по команде."""
    await update.message.reply_text("Okay, bye.")

    return END


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка окончания разговора по кнопке InlineKeyboardButton."""
    await update.callback_query.answer()

    text = "See you around!"
    await update.callback_query.edit_message_text(text=text)

    return END


async def end_describing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End gathering of features and return to parent conversation."""
    user_data = context.user_data
    level = user_data[CURRENT_LEVEL]
    if not user_data.get(level):
        user_data[level] = []
    user_data[level].append(user_data[FEATURES])

    user_data[START_OVER] = True
    await start(update, context)

    return END


async def stop_nested(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Completely end conversation from within nested conversation."""
    await update.message.reply_text("Okay, bye.")

    return STOPPING
