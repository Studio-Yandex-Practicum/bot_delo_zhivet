from json import JSONDecodeError
from urllib.parse import urljoin
from uuid import uuid4

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from structlog import contextvars
from telegram import Update
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler, ConversationHandler,
    InvalidCallbackData, MessageHandler, PicklePersistence, filters,
)
from telegram.ext.filters import Regex

from src.bot.const import (
    BECOME_VOLUNTEER_CMD, DATA_PATH, END_CMD, MAKE_DONATION_CMD,
    REPORT_ECO_PROBLEM_CMD, SAVE_PERSISTENCE_INTERVAL,
    SPECIFY_ACTIVITY_RADIUS_CMD, SPECIFY_ADDRESS_CMD,
    SPECIFY_CAR_AVAILABILITY_CMD, SPECIFY_PHONE_PERMISSION_CMD,
)
from src.bot.handlers.add_tags import (
    pollution_tags_handler, social_tags_handler,
)
from src.bot.handlers.common import (
    end_describing, handle_invalid_button, help_command, stop,
)
from src.bot.handlers.holiday import (
    endless_holiday_now_save, stop_holiday_now_save,
)
from src.bot.handlers.loggers import logger
from src.bot.handlers.participation import make_donation
from src.bot.handlers.pollution import (
    back_to_select_option_to_report_about_pollution, input, save_comment,
    save_foto, save_location, select_option_to_report_about_pollution,
)
from src.bot.handlers.social import (
    back_to_add_social, input_social_data, report_about_social_problem,
    save_social_address_input, save_social_problem_data,
)
from src.bot.handlers.start import start
from src.bot.handlers.state_constants import (
    ADD_POLLUTION_TAG, ADD_SOCIAL_TAG, ADDING_SOCIAL_TASK, ADDING_VOLUNTEER,
    ADDRESS_COMMAND, ADDRESS_INPUT, BACK, CAR_COMMAND, DADATA_UNAVAILABLE,
    ENDLESS_HOLIDAY_START_NOW, HOLIDAY_STOP_NOW, NO_TAG, PHONE_COMMAND,
    PHONE_INPUT, POLLUTION_COMMENT, POLLUTION_COORDINATES, POLLUTION_FOTO,
    RADIUS_COMMAND, SAVE, SELECTING_ACTION, SELECTING_FEATURE, SELECTING_OVER,
    SOCIAL_COMMENT, SOCIAL_PROBLEM_TYPING, TAG_ID_PATTERN, TYPING,
    TYPING_ADDRESS, VALIDATE,
)
from src.bot.handlers.volunteer import (
    add_volunteer, ask_user_phone_number, back_to_add_volunteer,
    handle_car_input, handle_phone_input, handle_radius_input, save_input,
)
from src.bot.service.common_functions import (
    address_confirmation, ask_for_input_address, retry_address_confirmation,
)
from src.bot.tasks import save_pollution, save_social_problem, save_volunteer
from src.core.config import settings


def create_bot() -> Application:
    """Создание приложения бота"""
    persistence = PicklePersistence(filepath=DATA_PATH, update_interval=SAVE_PERSISTENCE_INTERVAL)
    app = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .persistence(persistence)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )

    add_volunteer_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_volunteer, pattern=BECOME_VOLUNTEER_CMD)],
        states={
            ADDING_VOLUNTEER: [
                CallbackQueryHandler(ask_user_phone_number, pattern=SPECIFY_PHONE_PERMISSION_CMD),
                CallbackQueryHandler(ask_for_input_address, pattern=SPECIFY_ADDRESS_CMD),
                CallbackQueryHandler(handle_radius_input, pattern=SPECIFY_ACTIVITY_RADIUS_CMD),
                CallbackQueryHandler(handle_car_input, pattern=SPECIFY_CAR_AVAILABILITY_CMD),
                CallbackQueryHandler(save_volunteer, pattern="^" + SAVE + "$"),
                CallbackQueryHandler(endless_holiday_now_save, pattern=ENDLESS_HOLIDAY_START_NOW),
                CallbackQueryHandler(stop_holiday_now_save, pattern=HOLIDAY_STOP_NOW),
            ],
            TYPING_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_confirmation)],
            VALIDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone_input)],
            SELECTING_OVER: [
                CallbackQueryHandler(save_input, pattern="^" + PHONE_COMMAND),
                CallbackQueryHandler(save_input, pattern="^" + ADDRESS_COMMAND),
                CallbackQueryHandler(save_input, pattern="^" + RADIUS_COMMAND),
                CallbackQueryHandler(save_input, pattern="^" + CAR_COMMAND),
                CallbackQueryHandler(retry_address_confirmation, pattern=f"^{DADATA_UNAVAILABLE}$"),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(end_describing, pattern=END_CMD),
            CommandHandler("stop", stop),
            CallbackQueryHandler(ask_user_phone_number, pattern=PHONE_INPUT),
            CallbackQueryHandler(ask_for_input_address, pattern=ADDRESS_INPUT),
            CallbackQueryHandler(back_to_add_volunteer, pattern=BACK),
        ],
        persistent=True,
        name="add_volunteer_conv",
        allow_reentry=True,
    )

    add_pollution_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_option_to_report_about_pollution, pattern=REPORT_ECO_PROBLEM_CMD)],
        states={
            SELECTING_FEATURE: [
                CallbackQueryHandler(input, pattern="^" + POLLUTION_COMMENT + "$"),
                CallbackQueryHandler(input, pattern="^" + POLLUTION_COORDINATES + "$"),
                CallbackQueryHandler(input, pattern="^" + POLLUTION_FOTO + "$"),
                CallbackQueryHandler(save_pollution, pattern="^" + SAVE + "$"),
                CallbackQueryHandler(pollution_tags_handler.enter_tags, ADD_POLLUTION_TAG),
            ],
            TYPING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_comment),
                MessageHandler(filters.PHOTO & ~filters.COMMAND, save_foto),
                MessageHandler(filters.LOCATION & ~filters.COMMAND, save_location),
                MessageHandler(filters.ATTACHMENT & ~filters.COMMAND, save_foto),
            ],
            ADD_POLLUTION_TAG: [
                CallbackQueryHandler(pollution_tags_handler.enter_tags, TAG_ID_PATTERN),
                CallbackQueryHandler(pollution_tags_handler.no_tag, NO_TAG),
                CallbackQueryHandler(pollution_tags_handler.exit_tags, BACK),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(end_describing, pattern=END_CMD),
            CommandHandler("stop", stop),
            CallbackQueryHandler(input, pattern=POLLUTION_COMMENT),
            CallbackQueryHandler(input, pattern=POLLUTION_COORDINATES),
            CallbackQueryHandler(input, pattern=POLLUTION_FOTO),
            CallbackQueryHandler(back_to_select_option_to_report_about_pollution, pattern=BACK),
        ],
        persistent=True,
        name="add_pollution_conv",
        allow_reentry=True,
    )

    add_social_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                report_about_social_problem,
                pattern=ADDING_SOCIAL_TASK,
            )
        ],
        states={
            SELECTING_FEATURE: [
                CallbackQueryHandler(ask_for_input_address, pattern=SPECIFY_ADDRESS_CMD),
                CallbackQueryHandler(input_social_data, pattern="^" + SOCIAL_COMMENT + "$"),
                CallbackQueryHandler(save_social_problem, pattern="^" + SAVE + "$"),
                CallbackQueryHandler(social_tags_handler.enter_tags, ADD_SOCIAL_TAG),
            ],
            SOCIAL_PROBLEM_TYPING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_social_problem_data),
            ],
            SELECTING_OVER: [
                CallbackQueryHandler(save_social_address_input, pattern="^" + ADDRESS_COMMAND),
                CallbackQueryHandler(retry_address_confirmation, pattern=f"^{DADATA_UNAVAILABLE}$"),
            ],
            TYPING_ADDRESS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, address_confirmation),
            ],
            ADD_SOCIAL_TAG: [
                CallbackQueryHandler(social_tags_handler.enter_tags, TAG_ID_PATTERN),
                CallbackQueryHandler(social_tags_handler.no_tag, NO_TAG),
                CallbackQueryHandler(social_tags_handler.exit_tags, BACK),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(end_describing, pattern=END_CMD),
            CommandHandler("stop", stop),
            CallbackQueryHandler(ask_for_input_address, pattern=ADDRESS_INPUT),
            CallbackQueryHandler(back_to_add_social, pattern=BACK),
        ],
        persistent=True,
        name="add_social_conv",
        allow_reentry=True,
    )
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_ACTION: [
                add_volunteer_conv,
                add_pollution_conv,
                add_social_conv,
            ],
        },
        fallbacks=[CommandHandler("stop", stop)],
        persistent=True,
        name="conv_handler",
        allow_reentry=True,
    )

    app.add_handler(conv_handler)

    app.add_handler(MessageHandler(Regex(MAKE_DONATION_CMD), make_donation))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(handle_invalid_button, InvalidCallbackData))

    return app


def run_bot_polling() -> None:
    """Запуск бота в режиме polling"""
    bot_app = create_bot()
    bot_app.run_polling()
    logger.info("Start polling")


async def init_webhook() -> Application:
    """Инициализация вебхука"""
    bot_app = create_bot()
    bot_app.updater = None
    url = settings.WEBHOOK_DOMAIN + settings.WEBHOOK_PATH
    await bot_app.bot.set_webhook(url=url, secret_token=settings.TELEGRAM_BOT_TOKEN.replace(":", ""))
    await bot_app.initialize()
    await bot_app.start()
    logger.info("Webhook initialized", app_url=url)
    return bot_app


def run_bot_webhook():
    """Запуск бота в режиме webhook"""

    async def on_start_bot() -> None:
        bot_app = await init_webhook()
        starlette_app.state.bot_app = bot_app
        logger.info("The bot has been started")

    async def on_stop_bot() -> None:
        await starlette_app.state.bot_app.stop()
        await starlette_app.state.bot_app.shutdown()
        logger.info("The bot has been stopped")

    async def webhook_api(request: Request) -> Response:
        """Обработка входящих обновлений и помещение их в очередь"""
        response = {}
        try:
            request_json = await request.json()
            bot_app = request.app.state.bot_app
            contextvars.clear_contextvars()
            contextvars.bind_contextvars(request_id=str(uuid4()))
            logger.info("REQUEST", request_data=request_json)
            await bot_app.update_queue.put(Update.de_json(data=request_json, bot=bot_app.bot))
        except JSONDecodeError as error:
            logger.error("Got a JSONDecodeError:", error=error)
            response = {"status_code": httpx.codes.BAD_REQUEST}

        return Response(**response)

    def get_routes() -> list[Route]:
        """Список маршрутов"""
        routes = [
            Route(settings.WEBHOOK_PATH, webhook_api, methods=["POST"]),
        ]
        return routes

    starlette_app = Starlette(
        routes=get_routes(),
        on_startup=[on_start_bot],
        on_shutdown=[on_stop_bot],
        debug=True,
    )
    uvicorn.run(app=starlette_app, host=settings.HOST, port=settings.WEBHOOK_PORT)


def start_bot() -> None:
    # Если в файле .env.telegram есть такие настройки, то запустится webhook
    if settings.WEBHOOK_DOMAIN and settings.WEBHOOK_PORT:
        run_bot_webhook()
    else:
        run_bot_polling()
