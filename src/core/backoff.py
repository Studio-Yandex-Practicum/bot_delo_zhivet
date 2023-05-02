import backoff
from structlog import get_logger

from core.config import settings

logger = get_logger(settings.logger_name)

"""
Base_method - арифметическая прогрессия.
RandomJitter_method - арифметическая прогрессия
                    с добавлением случайного числа милисекунд.
FullJitter_method - алгоритм «Full Jitter», определенный в публикации
        «Экспоненциальное отставание и джиттер» в блоге об архитектуре AWS.
"""
JITTER = {"Base_method": None, "RandomJitter_method": backoff.random_jitter, "FullJitter_method": backoff.full_jitter}


def backoff_hdlr(details):
    logger.error(
        "Database crash",
        tries=details.get("tries"),
        wait_time=float("{:.3f}".format(details.get("wait"))),
        total_waiting_time=float("{:.3f}".format(details.get("elapsed"))),
    )
