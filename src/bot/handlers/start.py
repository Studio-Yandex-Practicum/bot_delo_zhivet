from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      KeyboardButton, ReplyKeyboardMarkup, Update)
from telegram.ext import ContextTypes

from bot import const
from bot.handlers import state_constants

GREETING_MESSAGE = (
    'Привет, {username}. Я бот экологического проекта "Дело живёт".'
    " Я могу принять заявку на помощь, или зарегистрировать тебя волонтером."
    " Выбери необходимое действие."
)

BYE_MESSAGE = "До свидания, {username}. Возвращайтесь в любой момент." 'Фонд "Дело живёт" ждёт тебя.'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправка сообщения с кнопками главного меню"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="Сообщить о социальной проблеме",
                callback_data=const.REPORT_SOCIAL_PROBLEM_CMD),
            InlineKeyboardButton(
                text="Сообщить о экологической проблеме",
                callback_data=const.REPORT_ECO_PROBLEM_CMD),
        ],
        [
            InlineKeyboardButton(
                text="Стать волонтёром",
                callback_data=const.BECOME_VOLUNTEER_CMD),
            InlineKeyboardButton(
                text="Сделать пожертвование",
                callback_data=const.MAKE_DONATION_CMD),
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
