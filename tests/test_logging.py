"""Test."""
import json
import logging
import logging.config
import socket

from logging_opentelemetry_format.utils import OpentelemetryLogFormatter
from opentelemetry.sdk._logs import _RESERVED_ATTRS

global log_list

log_list = list()


# here list handler is used to perform testing easily, you can use any log handler in your code
class ListHandler(logging.Handler):
    """ListHandler."""

    def __init__(self, level=logging.NOTSET, **kwargs):
        """Init."""
        super().__init__(level, **kwargs)
        self.log_list = log_list

    def emit(self, record):
        """emit."""
        self.log_list.append(self.format(record))
        print(self.log_list[-1])


logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "list": {
            "level": "DEBUG",
            "()": ListHandler,
            "formatter": "opentelemetry_formatter"
        }
    },
    "formatters": {
        "opentelemetry_formatter": {
            "()": OpentelemetryLogFormatter,
            "use_traces": True,
            "restrict_attributes_to": [
                "key1", "key2", "key3"
            ],
            "discard_attributes_from": _RESERVED_ATTRS,
            "meta_character_limit": 100,
            "body_character_limit": 10,
            "resource_attributes": {
                "service.name": "app-main-server",
                "service.instance.id": socket.gethostname()
            }
        }
    },
    "loggers": {
        "": {
            "level": "DEBUG",
            "handlers": ["list"],
            "propagate": True
        }
    }
})

print("starting logging")
logger = logging.getLogger(__name__)


def _basic_assertions(logstring):
    log = json.loads(logstring)
    assert len(log["body"]) <= 10
    if "_meta" in log["attributes"]:
        assert len(log["attributes"]["_meta"]) <= 100

    assert log["resource"]["service.name"] == "app-main-server"
    assert type(log["resource"]["service.instance.id"]) == str


def test_logger():
    """test_logger."""
    logger.debug("test message", {"key1": "test", "metakey1": "metavalue1"})
    _basic_assertions(log_list[-1])
