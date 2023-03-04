from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.handlers.state_constants import (
    ADDING_ECO_TASK,
    ADDING_SOCIAL_TASK,
    ADDING_VOLUNTEER,
    GREETING_MESSAGE,
    SELECTING_ACTION,
    START_OVER,
    TOP_LEVEL_MENU_TEXT,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Выбор действия: Добавление проблемы/регистрация волонтера."""
    text = TOP_LEVEL_MENU_TEXT
    # Если пользователь отправляет именно КОМАНДУ старт, то очищаем его данные
    if update.message:
        context.user_data.clear()
        await context.application.persistence.drop_user_data(update.message.from_user["id"])
    buttons = [
        [
            InlineKeyboardButton(text="Сообщить об экологической проблеме", callback_data=ADDING_ECO_TASK),
        ],
        [
            InlineKeyboardButton(text="Сообщить о социальной проблеме", callback_data=ADDING_SOCIAL_TASK),
        ],
        [
            InlineKeyboardButton(text="Стать волонтером", callback_data=ADDING_VOLUNTEER),
        ],
        [
            InlineKeyboardButton(
                text="Сделать пожертвование", url="https://delozhivet.ru/campaign/pomoch-delo-zhivet/"
            ),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    print(
        f"""

         В ГЛАВНОМ МЕНЮ:
         {context.user_data}


         """
    )

    # Если пользователь в первый раз обращается к боту, то покажем ему приветственное сообщение
    if not context.user_data.get(START_OVER):
        user = update.message.from_user
        username = user["username"]
        if username:
            text = f"Привет, {username}! " + GREETING_MESSAGE
        else:
            text = "Привет! " + GREETING_MESSAGE
        await update.message.reply_text(text=text, reply_markup=keyboard)
    else:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False

    print(
        f"""

         В ГЛАВНОМ МЕНЮ:
         {context.user_data}

         """
    )

    return SELECTING_ACTION
