"""Formatters."""
import datetime
import json
import logging

from opentelemetry.sdk._logs import _RESERVED_ATTRS
from opentelemetry.sdk._logs.severity import std_to_otlp
from opentelemetry.trace import (
    format_span_id,
    format_trace_id,
    get_current_span
)
import pkg_resources
import ujson

logger = logging.getLogger(__name__)


class OpentelemetryLogFormatter(logging.Formatter):
    """OpentelemetryLogFormatter."""

    DEFAULT_RESOURCE = {
        "telemetry.sdk.language": "python",
        "telemetry.sdk.name": "opentelemetry",
        "telemetry.sdk.version": pkg_resources.get_distribution(
            "opentelemetry-sdk"
        ).version,
    }

    MISSING_BODY_MESSAGE = "MissingLogBody"

    BODY_TOO_LARGE_ATTRIBUTE_NAME = "_body_too_large"
    BODY_CHAR_LENGTH_ATTRIBUTE_NAME = "_body_original_length"

    META_ATTRIBUTE_NAME = "_meta"
    META_TOO_LARGE_ATTRIBUTE_NAME = "_meta_too_large"
    META_CHAR_LENGTH_ATTRIBUTE_NAME = "_meta_original_length"

    def __init__(self, **kwargs):
        """Init."""
        super().__init__()
        self.resource_attributes = kwargs.get("resource_attributes") or {}
        if not self.resource_attributes.get("service.name"):
            raise Exception("service.name is mandatory in resource_attributes")
        self.resource_attributes.update(self.DEFAULT_RESOURCE)
        self.use_traces = kwargs.get("use_traces")
        self.json_indent = kwargs.get("json_indent", 0)
        self.meta_character_limit = kwargs.get("meta_character_limit", 1000)
        self.body_character_limit = kwargs.get("body_character_limit", 500)

        self.restrict_attributes_to = {
            self.BODY_TOO_LARGE_ATTRIBUTE_NAME, self.BODY_CHAR_LENGTH_ATTRIBUTE_NAME,
            self.META_TOO_LARGE_ATTRIBUTE_NAME, self.META_CHAR_LENGTH_ATTRIBUTE_NAME
        }
        self.get_attributes = self.get_attributes_simple
        if kwargs.get("restrict_attributes_to"):
            self.get_attributes = self.get_attributes_structured
            self.restrict_attributes_to = self.restrict_attributes_to.union(
                kwargs.get("restrict_attributes_to")
            )
        self.discard_attributes_from = set(_RESERVED_ATTRS)
        if "discard_attributes_from" in kwargs:
            self.discard_attributes_from = set(kwargs.get("discard_attributes_from"))

    def get_attributes_structured(self, raw_attributes):
        """get_attributes_structured."""
        meta_attributes = dict()
        attributes = dict()
        for k, v in raw_attributes.items():
            if k in self.discard_attributes_from:
                continue
            if k in self.restrict_attributes_to:
                attributes[k] = v
            else:
                meta_attributes[k] = v
        exc_info = attributes.get("exc_info")
        if exc_info:
            attributes["exc_info"] = self.formatException(exc_info)
        if meta_attributes:
            meta_attributes = str(meta_attributes)
            if len(meta_attributes) > self.meta_character_limit:
                attributes[self.META_CHAR_LENGTH_ATTRIBUTE_NAME] = len(meta_attributes)
                attributes[self.META_TOO_LARGE_ATTRIBUTE_NAME] = True
                meta_attributes = meta_attributes[:self.meta_character_limit]
            attributes[self.META_ATTRIBUTE_NAME] = meta_attributes
        return attributes

    def get_attributes_simple(self, raw_attributes):
        """get_attributes_simple."""
        attributes = {k: raw_attributes[k] for k in raw_attributes if k not in self.discard_attributes_from}
        exc_info = attributes.get("exc_info")
        if exc_info:
            attributes["exc_info"] = self.formatException(exc_info)
        return attributes

    def get_trace_related_data(self):
        """get_trace_related_data."""
        if self.use_traces:
            span_context = get_current_span().get_span_context()
            return(span_context.trace_id, span_context.span_id, span_context.trace_flags)
        else:
            return ("", "", 0)

    def format(self, record):  # noqa: A003
        """format."""
        trace_id, span_id, trace_flags = self.get_trace_related_data()
        trace_id = format_trace_id(trace_id if trace_id else 0)
        span_id = format_span_id(span_id if span_id else 0)

        body = record.getMessage()
        raw_attributes = vars(record)
        if type(record.msg) == dict:
            raw_attributes.update(record.msg)
            body = self.MISSING_BODY_MESSAGE
        elif len(body) > self.body_character_limit:
            raw_attributes[self.BODY_CHAR_LENGTH_ATTRIBUTE_NAME] = len(body)
            raw_attributes[self.BODY_TOO_LARGE_ATTRIBUTE_NAME] = True
            body = body[:self.body_character_limit]

        record_dict = {
            "body": f"{body}",
            "severity_number": std_to_otlp(record.levelno).value,
            "severity_text": record.levelname,
            "attributes": self.get_attributes(raw_attributes),
            "timestamp": datetime.datetime.utcfromtimestamp(record.created).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "trace_id": trace_id,
            "span_id": span_id,
            "trace_flags": trace_flags,
            "resource": {
                "pathname": record.pathname,
                "lineno": record.lineno,
                **self.resource_attributes
            }
        }
        try:
            message_string = ujson.dumps(
                record_dict, indent=self.json_indent)
        except Exception as e:
            logger.exception(e)
            message_string = json.dumps(
                record_dict, indent=None, default=str)
        return message_string
