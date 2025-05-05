import logging
from logging import LogRecord
from typing import List

from swarmauri_base import register_type
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase


@register_type()
class KeyValueFormatter(FormatterBase):
    """
    A formatter that renders log record attributes as key=value pairs.

    This formatter outputs log messages in a structured format where each attribute
    is represented as a key-value pair, making it easier to parse logs programmatically.

    Attributes:
        key_value_separator: Character used to separate keys from values
        pair_delimiter: Character used to separate key-value pairs
        include_extra: Whether to include extra attributes from the LogRecord
        fields: List of fields to include in the output, in the desired order
        format: The format string (constructed dynamically)
        date_format: Format for timestamps
    """

    key_value_separator: str = "="
    pair_delimiter: str = " "
    include_extra: bool = False
    fields: List[str] = ["levelname", "name", "message"]
    format: str = "%(message)s"  # Will be overridden in model_post_init
    date_format: str = "%Y-%m-%d %H:%M:%S"

    def model_post_init(self, *args, **kwargs):
        """
        Initialize the formatter after the model is created.

        This method constructs the format string based on the configured fields
        and other parameters.
        """
        # The base format is constructed dynamically in compile_formatter
        # We just ensure format exists for compatibility with base class
        self.format = "%(message)s"

    def compile_formatter(self) -> logging.Formatter:
        """
        Create and return a custom logging.Formatter that formats records as key-value pairs.

        Returns:
            A logging Formatter instance that uses our custom format method
        """
        # Create a custom formatter that uses our format_record method
        formatter = logging.Formatter(self.format, self.date_format)
        formatter.format = self.format_record
        return formatter

    def format_record(self, record: LogRecord) -> str:
        """
        Format a log record as key-value pairs.

        Args:
            record: The LogRecord to format

        Returns:
            A formatted string with key-value pairs
        """
        # Dictionary to store the key-value pairs
        output_parts = []

        # Process the standard fields in the specified order
        for field in self.fields:
            if field == "message":
                # Special handling for message to ensure it's formatted
                value = record.getMessage()
            elif hasattr(record, field):
                value = getattr(record, field)
            else:
                continue

            # Add the key-value pair to our output
            output_parts.append(f"{field}{self.key_value_separator}{value}")

        # Include any extra attributes if specified
        if self.include_extra and hasattr(record, "extra"):
            extra = record.extra
            if isinstance(extra, dict):
                for key, value in extra.items():
                    if key not in self.fields:
                        output_parts.append(f"{key}{self.key_value_separator}{value}")

        # Include any non-standard attributes directly attached to the LogRecord
        if self.include_extra:
            for key, value in record.__dict__.items():
                # Skip standard attributes and internal ones (starting with _)
                if (
                    key not in self.fields
                    and not key.startswith("_")
                    and key
                    not in (
                        "args",
                        "exc_info",
                        "exc_text",
                        "stack_info",
                        "lineno",
                        "funcName",
                        "created",
                        "msecs",
                        "relativeCreated",
                        "levelno",
                        "msg",
                    )
                ):
                    output_parts.append(f"{key}{self.key_value_separator}{value}")

        # Join all parts with the specified delimiter
        return self.pair_delimiter.join(output_parts)
