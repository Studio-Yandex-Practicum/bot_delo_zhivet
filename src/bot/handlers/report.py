from telegram import Update
from telegram.ext import ContextTypes


async def report_social_problem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Раздел "Сообщить о социальной проблеме"')


async def report_eco_problem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Раздел "Сообщить о экологической проблеме"')
