from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.handlers import state_constants

GREETING_MESSAGE = (
    'Привет, {username}. Я бот экологического проекта "Дело живёт".'
    " Я могу принять заявку на помощь, или зарегистрировать тебя волонтером."
    " Выбери необходимое действие."
)

BYE_MESSAGE = "До свидания, {username}. Возращайтесь в любой момент." 'Фонд "Дело живёт" ждёт тебя.'


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

    if context.user_data.get(state_constants.START_OVER):
        await update.message.reply_text("Выберете действие", reply_markup=reply_markup)
    else:
        user = update.message.from_user
        username = user["username"]
        text = GREETING_MESSAGE.format(username=username)
        await update.message.reply_text(text=text, reply_markup=reply_markup)
    context.user_data[state_constants.START_OVER] = False
    return state_constants.TOP_MENU


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    await update.message.reply_text("help text")


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик команды /stop."""
    user = update.message.from_user
    username = user["username"]
    text = BYE_MESSAGE.format(username=username)
    await update.message.reply_text(text)

    return state_constants.END
