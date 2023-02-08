from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.bot.handlers.start import start
from src.bot.handlers.state_constants import CURRENT_LEVEL, END, MAKING_DONATION, START_OVER
from src.bot.service.save_new_user import create_new_user
from src.core.db.db import get_async_session


async def become_volunteer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # noqa
    await update.message.reply_text('Раздел "Стать волонтёром"')


async def make_donation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    session_generator = get_async_session()
    session = await session_generator.asend(None)
    await create_new_user(telegram_id, session)
    text = (
        "Счастье - это то, чего человек желает для себя одного;\n"
        "благо - это то, что человек желает для себя вместе со всеми.\n"
        "Л.Н. Толстой"
    )
    level = update.callback_query.data
    context.user_data[CURRENT_LEVEL] = level
    buttons = [
        [
            InlineKeyboardButton(
                text="Сайт для пожертвований", url="https://delozhivet.ru/campaign/pomoch-delo-zhivet/"
            ),
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return MAKING_DONATION


async def end_second_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Возврат к главному меню."""
    context.user_data[START_OVER] = True
    await start(update, context)
    return END
