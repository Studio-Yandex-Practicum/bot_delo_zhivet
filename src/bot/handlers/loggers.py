import logging
import sys

STR_FORMAT = "[%(asctime)s] %(filename)s:%(lineno)d [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(logger_name=__file__):
    """Создание и настройка логгера."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(fmt=STR_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
