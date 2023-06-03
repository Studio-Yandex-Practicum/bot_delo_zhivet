from functools import partial
from json import dumps
from os import getpid

import structlog
from structlog import PrintLogger
from structlog.contextvars import merge_contextvars
from structlog.processors import JSONRenderer, TimeStamper, UnicodeDecoder, add_log_level

from .config import Config

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


def add_pid(logger, log_method, event_dict):
    event_dict["pid"] = getpid()
    return event_dict


add_timestamp = TimeStamper(fmt=DATETIME_FORMAT, utc=False)

structlog.configure(
    processors=[
        merge_contextvars,
        add_pid,
        add_log_level,
        add_timestamp,
        UnicodeDecoder(),
        JSONRenderer(serializer=partial(dumps, ensure_ascii=False)),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(Config.LOG_DEFAULT_LVL),
)

logger: PrintLogger = structlog.getLogger("admin_logger")
