import logging
from typing import Any, Dict, List, Optional

from swarmauri_base import register_type
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase


@register_type()
class ContextualFormatter(FormatterBase):
    """
    A formatter that adds contextual information to log messages.

    This formatter enhances log messages by including contextual information
    such as request IDs, user IDs, or any other attributes attached to the
    LogRecord object.
    """

    format: str = "[%(name)s][%(levelname)s] %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"

    # Context keys to look for in the LogRecord
    context_keys: List[str] = ["request_id", "user_id", "correlation_id"]

    # Custom context keys can be added
    custom_context_keys: List[str] = []

    # Format context as key=value pairs or as a prefix
    context_as_prefix: bool = False

    # Separator between context items
    context_separator: str = " "

    # Prefix and suffix for the entire context section
    context_prefix: str = "["
    context_suffix: str = "]"

    # Format for each context item when not using prefix mode
    context_item_format: str = "{key}={value}"

    # Whether to include context when all values are missing
    include_empty_context: bool = False

    def model_post_init(self, *args, **kwargs):
        """
        Initialize the formatter after model creation.

        Combines the base format with context formatting logic.
        """
        # We'll modify the format string in compile_formatter
        super().model_post_init(*args, **kwargs)

    def compile_formatter(self) -> logging.Formatter:
        """
        Create and return a logging.Formatter with context handling.

        Returns:
            logging.Formatter: A formatter that will include context information.
        """
        # Create a custom formatter that processes context
        return ContextualFormatterImpl(
            fmt=self.format,
            datefmt=self.date_format,
            context_keys=self.context_keys + self.custom_context_keys,
            context_as_prefix=self.context_as_prefix,
            context_separator=self.context_separator,
            context_prefix=self.context_prefix,
            context_suffix=self.context_suffix,
            context_item_format=self.context_item_format,
            include_empty_context=self.include_empty_context,
        )

    def add_context_key(self, key: str) -> None:
        """
        Add a new context key to be included in log messages.

        Args:
            key: The name of the context key to add
        """
        if key not in self.context_keys and key not in self.custom_context_keys:
            self.custom_context_keys.append(key)


class ContextualFormatterImpl(logging.Formatter):
    """
    Implementation of the contextual formatter logic.

    This class extends the standard logging.Formatter to include
    contextual information from LogRecord attributes.
    """

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        context_keys: List[str] = None,
        context_as_prefix: bool = False,
        context_separator: str = " ",
        context_prefix: str = "[",
        context_suffix: str = "]",
        context_item_format: str = "{key}={value}",
        include_empty_context: bool = False,
        **kwargs,
    ):
        """
        Initialize the contextual formatter.

        Args:
            fmt: The base format string
            datefmt: The date format string
            context_keys: List of attribute names to extract from LogRecord
            context_as_prefix: Whether to format context as a prefix
            context_separator: Separator between context items
            context_prefix: Prefix for the entire context section
            context_suffix: Suffix for the entire context section
            context_item_format: Format for each context item (when not prefix mode)
            include_empty_context: Whether to include context section when all values are missing
            **kwargs: Additional arguments passed to logging.Formatter
        """
        super().__init__(fmt=fmt, datefmt=datefmt, **kwargs)
        self.context_keys = context_keys or ["request_id", "user_id"]
        self.context_as_prefix = context_as_prefix
        self.context_separator = context_separator
        self.context_prefix = context_prefix
        self.context_suffix = context_suffix
        self.context_item_format = context_item_format
        self.include_empty_context = include_empty_context

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the specified record as text with added context.

        Args:
            record: The log record to format

        Returns:
            str: The formatted log message with context
        """
        # First get the standard formatted message
        formatted_message = super().format(record)

        # Extract context values from the record
        context_values = {}
        for key in self.context_keys:
            # Check if the attribute exists in the record
            if hasattr(record, key):
                value = getattr(record, key)
                if value is not None:
                    context_values[key] = value

        # If no context values found and we don't include empty context, return the original message
        if not context_values and not self.include_empty_context:
            return formatted_message

        # Format the context section - even if empty with include_empty_context
        context_str = self._format_context(context_values)

        # For empty context with include_empty_context=True
        if not context_values and self.include_empty_context:
            context_str = f"{self.context_prefix}{self.context_suffix}"

        # Add the context to the message
        if self.context_as_prefix:
            # Add as prefix to the message
            return f"{context_str} {formatted_message}"
        else:
            # Add after the log level but before the message content
            if ": " in formatted_message:
                # Format like "INFO: [context] message"
                level_part, message_part = formatted_message.split(": ", 1)
                return f"{level_part}: {context_str} {message_part}"
            elif "] " in formatted_message:
                # Format like "[logger][INFO] [context] message"
                parts = formatted_message.split("] ", 1)
                return f"{parts[0]}] {context_str} {parts[1]}"
            else:
                # If we can't find the expected format, append to the end
                return f"{formatted_message} {context_str}"

    def _format_context(self, context_values: Dict[str, Any]) -> str:
        """
        Format the context values according to configuration.

        Args:
            context_values: Dictionary of context key-value pairs

        Returns:
            str: Formatted context string
        """
        if not context_values:
            return ""

        context_items = []

        if self.context_as_prefix:
            # Format as simple values for prefix mode
            context_items = [str(value) for value in context_values.values()]
        else:
            # Format as key=value pairs
            for key, value in context_values.items():
                context_items.append(
                    self.context_item_format.format(key=key, value=value)
                )

        # Join the items with the separator
        context_content = self.context_separator.join(context_items)

        # Add prefix and suffix
        return f"{self.context_prefix}{context_content}{self.context_suffix}"
