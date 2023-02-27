import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from bot.application import start_bot
from core.config import settings

# Logging бота активируется при инициализации logger в main.py
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

if settings.SENTRY_DSN_URL:
    sentry_logging = LoggingIntegration(
        level=logging.INFO,
        event_level=logging.ERROR,
    )
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN_URL,
        integrations=[
            sentry_logging,
        ],
        traces_sample_rate=1.0,
        environment="bot",
    )

if __name__ == "__main__":
    start_bot()
