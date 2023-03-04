import logging
from json import JSONDecodeError
from urllib.parse import urljoin

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    PicklePersistence,
    filters,
)
from telegram.ext.filters import Regex

from bot.const import (
    BECOME_VOLUNTEER_CMD,
    DATA_PATH,
    END_CMD,
    MAKE_DONATION_CMD,
    REPORT_ECO_PROBLEM_CMD,
    SAVE_PERSISTENCE_INTERVAL,
    SPECIFY_ACTIVITY_RADIUS_CMD,
    SPECIFY_CAR_AVAILABILITY_CMD,
    SPECIFY_CITY_CMD,
    SPECIFY_PHONE_PERMISSION_CMD,
)
from core.config import settings

from .handlers.common import end_describing, help_command, stop
from .handlers.participation import make_donation
from .handlers.pollution import (
    back_to_add_pollution,
    input,
    save_and_exit_pollution,
    save_comment,
    save_foto,
    save_location,
    select_option_to_report_about_pollution,
)
from .handlers.social import (
    address_confirmation,
    ask_for_input_address,
    back_to_add_social,
    input_social_data,
    report_about_social_problem,
    save_and_exit_from_social_problem,
    save_social_address_input,
    save_social_problem_data,
)
from .handlers.start import start
from .handlers.state_constants import (
    ADDING_SOCIAL_TASK,
    ADDING_VOLUNTEER,
    BACK,
    CAR_COMMAND,
    CITY_COMMAND,
    CITY_INPUT,
    CITY_SOCIAL,
    POLLUTION_COMMENT,
    POLLUTION_COORDINATES,
    POLLUTION_FOTO,
    RADIUS_COMMAND,
    SAVE,
    SELECTING_ACTION,
    SELECTING_FEATURE,
    SELECTING_OVER,
    SOCIAL_ADDRESS,
    SOCIAL_COMMENT,
    SOCIAL_PROBLEM_ADDRESS,
    SOCIAL_PROBLEM_TYPING,
    TYPING,
    TYPING_CITY,
    TYPING_SOCIAL_CITY,
)
from .handlers.volunteer import (
    add_volunteer,
    ask_for_input_city,
    ask_user_phone_number,
    back_to_add_voluteer,
    handle_car_input,
    handle_city_input,
    handle_radius_input,
    save_and_exit_volunteer,
    save_input,
    save_phone,
)


def create_bot() -> Application:
    """Создание приложения бота"""
    persistence = PicklePersistence(filepath=DATA_PATH, update_interval=SAVE_PERSISTENCE_INTERVAL)
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).persistence(persistence).build()

    add_volunteer_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_volunteer, pattern=BECOME_VOLUNTEER_CMD)],
        states={
            ADDING_VOLUNTEER: [
                CallbackQueryHandler(ask_user_phone_number, pattern=SPECIFY_PHONE_PERMISSION_CMD),
                CallbackQueryHandler(ask_for_input_city, pattern=SPECIFY_CITY_CMD),
                CallbackQueryHandler(handle_radius_input, pattern=SPECIFY_ACTIVITY_RADIUS_CMD),
                CallbackQueryHandler(handle_car_input, pattern=SPECIFY_CAR_AVAILABILITY_CMD),
                CallbackQueryHandler(save_and_exit_volunteer, pattern="^" + SAVE + "$"),
            ],
            TYPING_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_city_input)],
            SELECTING_OVER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_phone),
                CallbackQueryHandler(save_input, pattern="^" + CITY_COMMAND),
                CallbackQueryHandler(save_input, pattern="^" + RADIUS_COMMAND),
                CallbackQueryHandler(save_input, pattern="^" + CAR_COMMAND),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(end_describing, pattern=END_CMD),
            CommandHandler("stop", stop),
            CallbackQueryHandler(ask_for_input_city, pattern=CITY_INPUT),
            CallbackQueryHandler(back_to_add_voluteer, pattern=BACK),
            CallbackQueryHandler(save_phone, pattern=BACK),
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
                CallbackQueryHandler(save_and_exit_pollution, pattern="^" + SAVE + "$"),
            ],
            TYPING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_comment),
                MessageHandler(filters.PHOTO & ~filters.COMMAND, save_foto),
                MessageHandler(filters.LOCATION & ~filters.COMMAND, save_location),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(end_describing, pattern=END_CMD),
            CommandHandler("stop", stop),
            CallbackQueryHandler(back_to_add_pollution, pattern=BACK),
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
                CallbackQueryHandler(ask_for_input_address, pattern="^" + SOCIAL_ADDRESS + "$"),
                CallbackQueryHandler(input_social_data, pattern="^" + SOCIAL_COMMENT + "$"),
                CallbackQueryHandler(save_and_exit_from_social_problem, pattern="^" + SAVE + "$"),
            ],
            SOCIAL_PROBLEM_TYPING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_social_problem_data),
            ],
            SOCIAL_PROBLEM_ADDRESS: [CallbackQueryHandler(save_social_address_input, pattern="^" + CITY_SOCIAL)],
            TYPING_SOCIAL_CITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, address_confirmation),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(end_describing, pattern=END_CMD),
            CommandHandler("stop", stop),
            CallbackQueryHandler(ask_for_input_address, pattern=CITY_INPUT),
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

    return app


def run_bot_polling() -> None:
    """Запуск бота в режиме polling"""
    bot_app = create_bot()
    bot_app.run_polling()
    aps_logger = logging.getLogger("apscheduler")
    aps_logger.setLevel(logging.DEBUG)
    aps_logger.info("Start polling")


async def init_webhook() -> Application:
    """Инициализация вебхука"""
    bot_app = create_bot()
    bot_app.updater = None
    url = urljoin(settings.WEBHOOK_DOMAIN, settings.WEBHOOK_PATH)
    await bot_app.bot.set_webhook(url=url, secret_token=settings.TELEGRAM_BOT_TOKEN.replace(":", ""))
    await bot_app.initialize()
    await bot_app.start()
    aps_logger = logging.getLogger("apscheduler")
    aps_logger.setLevel(logging.INFO)
    aps_logger.info(f"Webhook is. Application url: {url}")
    return bot_app


def run_bot_webhook():
    """Запуск бота в режиме webhook"""
    aps_logger = logging.getLogger("apscheduler")
    aps_logger.setLevel(logging.DEBUG)

    async def on_start_bot() -> None:
        bot_app = await init_webhook()
        starlette_app.state.bot_app = bot_app
        aps_logger.info("The bot has been started")

    async def on_stop_bot() -> None:
        await starlette_app.state.bot_app.stop()
        await starlette_app.state.bot_app.shutdown()
        aps_logger.info("The bot has been stopped")

    async def webhook_api(request: Request) -> Response:
        """Обработка входящих обновлений и помещение их в очередь"""
        response = {}
        try:
            request_json = await request.json()
            bot_app = request.app.state.bot_app
            await bot_app.update_queue.put(Update.de_json(data=request_json, bot=bot_app.bot))
        except JSONDecodeError as error:
            aps_logger.error("Got a JSONDecodeError: %s", error)
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
    # Если в файле .env есть такие настройки, то запустится webhook
    if settings.WEBHOOK_DOMAIN and settings.WEBHOOK_PORT:
        run_bot_webhook()
    else:
        run_bot_polling()
