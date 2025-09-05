from swarmauri_base import register_type
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
import logging
from typing import Optional


@register_type()
class MultilineFormatter(FormatterBase):
    """
    A formatter that ensures consistent formatting for multi-line log messages.

    This formatter prefixes each line of a multi-line log message with the
    configured timestamp and log level information to maintain readability
    and consistent structure in log files.
    """

    format: str = "[%(name)s][%(levelname)s] %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    include_timestamp: bool = True
    prefix_subsequent_lines: bool = True
    subsequent_line_prefix: Optional[str] = None
    indent_subsequent_lines: int = 0

    def model_post_init(self, *args, **kwargs):
        """
        Initialize the formatter after the model is created.

        Builds the format string based on configuration options.
        """
        format_parts = []

        if self.include_timestamp:
            format_parts.append("%(asctime)s")

        format_parts.append("[%(name)s]")
        format_parts.append("[%(levelname)s]")
        format_parts.append("%(message)s")

        self.format = " ".join(format_parts)

        # Calculate the prefix for subsequent lines if enabled
        if self.prefix_subsequent_lines and not self.subsequent_line_prefix:
            # Create a placeholder message to determine prefix length
            placeholder_record = logging.LogRecord(
                name="placeholder",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="",
                args=(),
                exc_info=None,
            )

            # Create a basic formatter to calculate prefix length
            basic_formatter = logging.Formatter(self.format, self.date_format)
            formatted_msg = basic_formatter.format(placeholder_record)

            # The prefix is everything before the actual message
            self.subsequent_line_prefix = " " * len(
                formatted_msg.split("%(message)s")[0]
            )

    def compile_formatter(self) -> logging.Formatter:
        """
        Create and return a custom logging.Formatter with multi-line support.

        Returns:
            logging.Formatter: A formatter that handles multi-line messages.
        """
        return _MultilineFormatterImpl(
            fmt=self.format,
            datefmt=self.date_format,
            prefix_subsequent_lines=self.prefix_subsequent_lines,
            subsequent_line_prefix=self.subsequent_line_prefix,
            indent_subsequent_lines=self.indent_subsequent_lines,
        )


class _MultilineFormatterImpl(logging.Formatter):
    """
    Internal implementation of the multiline formatter.

    This class extends the standard logging.Formatter to handle
    multi-line messages with proper prefixing.
    """

    def __init__(
        self,
        fmt=None,
        datefmt=None,
        style="%",
        prefix_subsequent_lines=True,
        subsequent_line_prefix=None,
        indent_subsequent_lines=0,
    ):
        """
        Initialize the multiline formatter.

        Args:
            fmt: Format string for log messages
            datefmt: Date format string
            style: Style of the format string (%, {, or $)
            prefix_subsequent_lines: Whether to prefix lines after the first
            subsequent_line_prefix: Custom prefix for lines after the first
            indent_subsequent_lines: Number of spaces to indent subsequent lines
        """
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.prefix_subsequent_lines = prefix_subsequent_lines
        self.subsequent_line_prefix = subsequent_line_prefix
        self.indent_subsequent_lines = indent_subsequent_lines

    def format(self, record):
        """
        Format the log record with multi-line support.

        This method overrides the standard format method to handle
        multi-line messages by prefixing each line appropriately.

        Args:
            record: The log record to format

        Returns:
            str: The formatted log message
        """
        # First format the record using the standard formatter
        formatted_message = super().format(record)

        # If there are no newlines, just return the formatted message
        if "\n" not in formatted_message:
            return formatted_message

        # Split the message into lines
        lines = formatted_message.splitlines()
        first_line = lines[0]

        # If we're not prefixing subsequent lines, just join them with newlines
        if not self.prefix_subsequent_lines:
            # Add indentation if configured
            if self.indent_subsequent_lines > 0:
                indent = " " * self.indent_subsequent_lines
                return (
                    first_line + "\n" + "\n".join(indent + line for line in lines[1:])
                )
            return "\n".join(lines)

        # Determine the prefix for subsequent lines
        if self.subsequent_line_prefix is not None:
            prefix = self.subsequent_line_prefix
        else:
            # Find where the actual message starts in the first line
            original_msg = record.getMessage()
            prefix_length = formatted_message.find(original_msg.split("\n")[0])
            prefix = " " * prefix_length

        # Add indentation if configured
        if self.indent_subsequent_lines > 0:
            prefix += " " * self.indent_subsequent_lines

        # Join all lines with the appropriate prefix
        result = [first_line]
        for line in lines[1:]:
            result.append(f"{prefix}{line}")

        return "\n".join(result)
