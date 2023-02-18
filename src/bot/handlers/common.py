from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.start import start
from bot.handlers.state_constants import END, START_OVER, STOPPING


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Спасибо! Нажми на /start, когда я снова понадоблюсь.")

    return END


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершить вложенную беседу"""
    await update.callback_query.answer()

    text = "Увидимся!"
    await update.callback_query.edit_message_text(text=text)

    return END


async def end_describing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Прекращение ввода и возврат в родительский диалог"""
    context.user_data[START_OVER] = True
    await start(update, context)

    return END


async def stop_nested(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Завершить беседу из вложенного разговора"""
    await update.message.reply_text("До свидания!")

    return STOPPING


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    await update.message.reply_text("help text")
