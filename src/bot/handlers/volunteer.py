from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes


async def volunteer(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Регистрация волонтера"""
    keyboard = [
        KeyboardButton("Сообщите свой город"),
        KeyboardButton("Сообщите радиус на который готовы выезжать"),
        KeyboardButton("У вас есть автомобиль, варианты: да/ нет")
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Заполните информацию о себе", reply_markup=reply_markup
    )
