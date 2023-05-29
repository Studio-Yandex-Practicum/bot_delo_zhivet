from telegram import Update
from telegram.ext import ContextTypes


# что это ??? оно никуда не импортится и нигде не вызывается
async def become_volunteer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Раздел "Стать волонтёром"')


async def make_donation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Раздел "Сделать пожертвование"')
