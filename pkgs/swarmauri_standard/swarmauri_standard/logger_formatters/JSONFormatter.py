import datetime
import json
import logging
from typing import Any, Dict

from swarmauri_base import register_type
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase


@register_type()
class JSONFormatter(FormatterBase):
    """
    JSON formatter for log records.

    This formatter converts log records into JSON strings, making logs easily parseable
    by log aggregation and analysis tools. Each log record is serialized as a JSON object
    containing standard fields like timestamp, log level, logger name, and message.

    Attributes
    ----------
    include_timestamp : bool
        Whether to include the timestamp in the JSON output. Default is True.
    include_exception : bool
        Whether to include exception information when present. Default is True.
    date_format : str
        The format string for the timestamp. Default is ISO8601 format.
    """

    include_timestamp: bool = True
    include_exception: bool = True
    date_format: str = "%Y-%m-%dT%H:%M:%S.%fZ"  # ISO8601 format

    def compile_formatter(self) -> logging.Formatter:
        """
        Create and return a custom JSON formatter.

        Returns
        -------
        logging.Formatter
            A formatter that outputs log records as JSON strings.
        """
        return _JSONLogFormatter(self)


class _JSONLogFormatter(logging.Formatter):
    """
    Internal class that handles the actual formatting of log records to JSON.

    This class is not meant to be used directly but is created by JSONFormatter.
    """

    def __init__(self, config: JSONFormatter):
        """
        Initialize the JSON formatter with configuration.

        Parameters
        ----------
        config : JSONFormatter
            The configuration for this formatter.
        """
        super().__init__()
        self.config = config

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as a JSON string.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to format.

        Returns
        -------
        str
            A JSON string representation of the log record.
        """
        # Create a base dictionary with the core log record attributes
        log_data: Dict[str, Any] = {
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }

        # Add timestamp if configured
        if self.config.include_timestamp:
            # Format the timestamp according to the configured date format
            if hasattr(record, "created"):
                timestamp = datetime.datetime.fromtimestamp(
                    record.created, tz=datetime.timezone.utc
                ).strftime(self.config.date_format)
                log_data["timestamp"] = timestamp

        # Add exception information if present and configured
        if self.config.include_exception and record.exc_info:
            # Format the exception info
            exc_info = self.formatException(record.exc_info)
            if exc_info:
                log_data["exception"] = exc_info

        # Add any custom fields from the record
        self._add_custom_fields(record, log_data)

        # Serialize to JSON with proper escaping
        try:
            return json.dumps(log_data)
        except (TypeError, ValueError) as e:
            # If JSON serialization fails, return a fallback message
            return json.dumps(
                {
                    "level": "ERROR",
                    "name": "JSONFormatter",
                    "message": f"Failed to serialize log record: {str(e)}",
                    "original_message": str(record.getMessage()),
                }
            )

    def _add_custom_fields(
        self, record: logging.LogRecord, log_data: Dict[str, Any]
    ) -> None:
        """
        Add any custom fields from the log record to the log data.

        Parameters
        ----------
        record : logging.LogRecord
            The log record containing potential custom fields.
        log_data : Dict[str, Any]
            The dictionary to add custom fields to.
        """
        # If the record has extra attributes, add them to the log data
        for key, value in record.__dict__.items():
            # Skip standard LogRecord attributes and private attributes
            if key not in [
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "id",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            ] and not key.startswith("_"):
                try:
                    # Try to add the value directly, if it's JSON serializable
                    json.dumps({key: value})
                    log_data[key] = value
                except (TypeError, ValueError):
                    # If not serializable, convert to string
                    log_data[key] = str(value)
