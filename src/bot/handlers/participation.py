from telegram import InputTextMessageContent, Update  # noqa
from telegram.ext import ContextTypes

from src.bot.handlers.state_constants import FEATURES, START_OVER, TELEGRAM_ID  # noqa
from src.bot.service.save_new_user import create_new_user
from src.core.db.db import get_async_session


async def become_volunteer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # noqa
    await update.message.reply_text('Раздел "Стать волонтёром"')


async def make_donation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # context.user_data[START_OVER] = True
    # user_data = context.user_data[FEATURES]
    # user_data[TELEGRAM_ID] = update.effective_user.id
    something = context.user_data
    something_1 = context.user_data[START_OVER]  # noqa
    print(type(something))
    telegram_id = update.effective_user.id
    print(type(telegram_id))
    session_generator = get_async_session()
    session = await session_generator.asend(None)
    print("+__+")
    await create_new_user(telegram_id, session)
    await update.message.reply_text("https://delozhivet.ru/campaign/pomoch-delo-zhivet/")
