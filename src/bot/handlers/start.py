from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.handlers.state_constants import (
    ADDING_ECO_TASK,
    ADDING_SOCIAL_TASK,
    ADDING_VOLUNTEER,
    MAKING_DONATION,
    SELECTING_ACTION,
    START_OVER,
    TOP_LEVEL_MENU_TEXT,
)

GREETING_MESSAGE = (
    'Привет, {username}. Я бот экологического проекта "Дело живёт".'
    " Я могу принять заявку на помощь, или зарегистрировать тебя волонтером."
    " Выбери необходимое действие."
)

BYE_MESSAGE = "До свидания, {username}. Возвращайся в любой момент." 'Фонд "Дело живёт" ждёт тебя.'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Выбор действия: Добавление проблемы/регистрация волонтера."""
    text = TOP_LEVEL_MENU_TEXT

    buttons = [
        [
            InlineKeyboardButton(text="Сообщить о социальной проблеме", callback_data=ADDING_SOCIAL_TASK),
        ],
        [
            InlineKeyboardButton(text="Сообщить об эко проблеме", callback_data=ADDING_ECO_TASK),
        ],
        [
            InlineKeyboardButton(text="Стать волонтером", callback_data=ADDING_VOLUNTEER),
            InlineKeyboardButton(text="Сделать пожертвование", callback_data=MAKING_DONATION),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    # Если пользователь в первый раз обращается к боту, то покажем ему приветственное сообщение
    context.user_data.get(START_OVER)
    if not context.user_data.get(START_OVER):
        user = update.message.from_user
        username = user["username"]
        text = GREETING_MESSAGE.format(username=username)
        await update.message.reply_text(text=text, reply_markup=keyboard)
    else:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_ACTION
