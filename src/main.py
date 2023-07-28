import logging

import sentry_sdk
import structlog
from sentry_sdk.integrations.logging import LoggingIntegration

from bot.application import start_bot
from core.config import settings

# Logging бота активируется при инициализации logger в main.py
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.processors.JSONRenderer(),
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
)

if settings.SENTRY_DSN_BOT:
    sentry_logging = LoggingIntegration(
        level=logging.INFO,
        event_level=logging.ERROR,
    )
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN_BOT,
        integrations=[
            sentry_logging,
        ],
        traces_sample_rate=1.0,
        environment="bot",
    )

    logger = structlog.get_logger("bot", processors=[structlog.stdlib.add_log_level, sentry_logging])
else:
    logger = structlog.get_logger("bot")

if __name__ == "__main__":
    logger.info("Starting bot")
    start_bot(logger)
