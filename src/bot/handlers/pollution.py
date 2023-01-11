from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes


async def pollution(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Сообщение о загрязнении"""
    keyboard = [
        KeyboardButton("Загрузите фото"),
        KeyboardButton("Укажите координаты"),
        KeyboardButton("Добавьте комментарий")
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Заполните информацию о загрязнении", reply_markup=reply_markup
    )
