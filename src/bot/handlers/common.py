from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.start import start
from bot.handlers.state_constants import END, HELP_TEXT, SITE_INFO, START_OVER, STOP_TEXT


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await context.application.persistence.drop_user_data(update.message.from_user["id"])
    await update.message.reply_text(STOP_TEXT)

    return END


async def end_describing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Прекращение ввода и возврат в родительский диалог"""
    context.user_data[START_OVER] = True
    await start(update, context)

    return END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    await update.message.reply_text(HELP_TEXT.format(site_info=SITE_INFO))
