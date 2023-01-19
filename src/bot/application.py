import logging

from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, filters
from telegram.ext.filters import Regex

from bot.const import (
    BECOME_VOLUNTEER_CMD,
    END_CMD,
    MAKE_DONATION_CMD,
    SPECIFY_ACTIVITY_RADIUS_CMD,
    SPECIFY_CAR_AVAILABILITY_CMD,
    SPECIFY_CITY_CMD,
)
from core.settings import settings

from .handlers.common import end_describing, stop, stop_nested
from .handlers.participation import make_donation
from .handlers.start import help_command, start
from .handlers.state_constants import (
    ADDING_VOLUNTEER,
    CAR_COMMAND,
    CITY_COMMAND,
    RADIUS_COMMAND,
    SELECTING_ACTION,
    SELECTING_OVER,
    TYPING_CITY,
)
from .handlers.volunteer import (
    add_volunteer,
    ask_for_input_city,
    handle_car_input,
    handle_city_input,
    handle_radius_input,
    save_input,
)


def start_bot() -> None:
    """Запуск бота"""
    aps_logger = logging.getLogger("apscheduler")
    aps_logger.setLevel(logging.DEBUG)
    bot = Application.builder().token(settings.telegram_bot_token).build()
    add_volunteer_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_volunteer, pattern=BECOME_VOLUNTEER_CMD)],
        states={
            ADDING_VOLUNTEER: [
                CallbackQueryHandler(ask_for_input_city, pattern=SPECIFY_CITY_CMD),
                CallbackQueryHandler(handle_radius_input, pattern=SPECIFY_ACTIVITY_RADIUS_CMD),
                CallbackQueryHandler(handle_car_input, pattern=SPECIFY_CAR_AVAILABILITY_CMD),
            ],
            TYPING_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_city_input)],
            SELECTING_OVER: [
                CallbackQueryHandler(save_input, pattern="^" + CITY_COMMAND),
                CallbackQueryHandler(save_input, pattern="^" + RADIUS_COMMAND),
                CallbackQueryHandler(save_input, pattern="^" + CAR_COMMAND),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(end_describing, pattern=END_CMD),
            CommandHandler("stop", stop_nested),
        ],
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_ACTION: [
                add_volunteer_conv,
            ],
        },
        fallbacks=[CommandHandler("stop", stop)],
    )

    bot.add_handler(conv_handler)

    bot.add_handler(MessageHandler(Regex(MAKE_DONATION_CMD), make_donation))
    bot.add_handler(CommandHandler("help", help_command))

    aps_logger.info("Service started.")

    bot.run_polling()

    aps_logger.info("Service stopped.")
