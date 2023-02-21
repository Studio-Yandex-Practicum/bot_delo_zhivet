import logging
import os
import sys

from .config import Config


def get_logger(file, display=False):

    """Создание и настройка логгера."""

    log_file = os.path.join(
        os.path.join(os.path.dirname(file), Config.LOG_REL_PATH), os.path.basename(file) + Config.LOG_EXTENSION
    )

    logger = logging.getLogger(os.path.basename(file))
    formatter = logging.Formatter(Config.LOG_FORMAT)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(Config.LOG_DEFAULT_LVL)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    if display:
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setLevel(Config.LOG_DEFAULT_LVL)
        console_handler.setFormatter(formatter)

    return logger
