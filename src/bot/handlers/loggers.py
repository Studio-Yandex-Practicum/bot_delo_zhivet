import logging
from functools import partial
from json import dumps
from os import getpid
from typing import TextIO

import structlog
from structlog import PrintLogger
from structlog.contextvars import merge_contextvars
from structlog.processors import (
    add_log_level, TimeStamper, UnicodeDecoder, JSONRenderer
)

from core.config import settings

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


class _DualWriter(TextIO):
    def __init__(self, filename, mode="a", encoding="utf-8"):
        self._filename = filename
        self._mode = mode
        self._encoding = encoding

    def write(self, data):
        with open(
                file=self._filename,
                mode=self._mode,
                encoding=self._encoding,
        ) as file:
            file.write(data)
            print(data, end="")

    def __getattr__(self, item):
        return self.pass_

    def pass_(self, *args, **kwargs):
        pass


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
    logger_factory=lambda *args: PrintLogger(
        file=_DualWriter(
            filename=settings.log_file,
            encoding=settings.log_encoding,
        )
    ),
    wrapper_class=structlog.make_filtering_bound_logger(settings.log_level)
)

logger: PrintLogger = structlog.getLogger(settings.logger_name)

