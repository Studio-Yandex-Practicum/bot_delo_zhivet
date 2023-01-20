from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.start import start
from bot.handlers.state_constants import (CURRENT_LEVEL, END, FEATURES,
                                          START_OVER, STOPPING)


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text("Ок, пока")

    return END


async def end(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """Завершить вложенную беседу"""
    await update.callback_query.answer()

    text = "Увидимся!"
    await update.callback_query.edit_message_text(text=text)

    return END


async def end_describing(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Прекращение ввода и возврат в родительский диалог"""

    await start(update, context)

    return END


async def stop_nested(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """Полностью завершить беседу из вложенного разговора"""
    await update.message.reply_text("Ок, пока!")

    return STOPPING


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    await update.message.reply_text("help text")
