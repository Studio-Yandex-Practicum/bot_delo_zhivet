from telegram.ext import Application, CommandHandler, MessageHandler
from telegram.ext.filters import Regex

from bot.const import BECOME_VOLUNTEER_CMD, MAKE_DONATION_CMD, REPORT_ECO_PROBLEM_CMD, REPORT_SOCIAL_PROBLEM_CMD
from core.settings import settings

from .handlers.participation import become_volunteer, make_donation
from .handlers.report import report_eco_problem, report_social_problem
from .handlers.start import help_command, start


def start_bot() -> None:
    """Запуск бота"""
    bot = Application.builder().token(settings.telegram_bot_token).build()

    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(MessageHandler(Regex(REPORT_SOCIAL_PROBLEM_CMD), report_social_problem))
    bot.add_handler(MessageHandler(Regex(REPORT_ECO_PROBLEM_CMD), report_eco_problem))
    bot.add_handler(MessageHandler(Regex(BECOME_VOLUNTEER_CMD), become_volunteer))
    bot.add_handler(MessageHandler(Regex(MAKE_DONATION_CMD), make_donation))
    bot.add_handler(CommandHandler("help", help_command))

    bot.run_polling()
