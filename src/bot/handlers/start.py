from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправка сообщения с кнопками главного меню"""
    keyboard = [
        [
            KeyboardButton("Сообщить о социальной проблеме"),
            KeyboardButton("Сообщить о экологической проблеме"),
        ],
        [
            KeyboardButton("Стать волонтёром"),
            KeyboardButton("Сделать пожертвование"),
        ],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберете действие", reply_markup=reply_markup
    )


async def help_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Обработчик команды /help."""
    await update.message.reply_text("help text")
