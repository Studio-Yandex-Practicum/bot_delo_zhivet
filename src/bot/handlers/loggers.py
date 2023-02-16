import logging
import sys

STR_FORMAT = "[%(asctime)s] %(filename)s:%(lineno)d " "[%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(logger_name=__file__):
    """Создание и настройка логгера."""
    # Create a custom logger
    logger = logging.getLogger(logger_name)
    # Create handlers
    console_handler = logging.StreamHandler(stream=sys.stdout)
    file_handler = logging.FileHandler("ERRORS_file.log")
    # Create levels
    console_handler.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.ERROR)
    # Create formatters
    formatter = logging.Formatter(fmt=STR_FORMAT, datefmt=DATE_FORMAT)
    error_formatter = logging.Formatter("%(asctime)s - %(name)s "
                                        "- %(levelname)s %(message)s")
    # Add formatters to handlers
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(error_formatter)
    # Add handlers to  the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
