from swarmauri_base import register_type
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
import logging
from typing import Optional


@register_type()
class IndentedFormatter(FormatterBase):
    """
    A formatter that adds indentation to each line of a log message.

    This formatter preserves the original message formatting while adding
    indentation to improve readability of multi-line log messages.

    Attributes:
        indent_width: Number of spaces to use for indentation.
        indent_first_line: Whether to indent the first line of the message.
        format: The log message format string.
        date_format: The date format string for timestamps.
    """

    indent_width: int = 4
    indent_first_line: bool = False
    format: str = "[%(name)s][%(levelname)s] %(message)s"
    date_format: Optional[str] = None

    def compile_formatter(self) -> logging.Formatter:
        """
        Create and return a logging.Formatter with indentation functionality.

        Returns:
            A custom logging.Formatter that adds indentation to log messages.
        """
        # Create a custom formatter that inherits from logging.Formatter
        parent_formatter = super().compile_formatter()

        # Create a wrapper class to modify the formatting behavior
        class IndentedLoggingFormatter(logging.Formatter):
            def __init__(self, parent_fmt, indent_width, indent_first_line):
                self.parent_formatter = parent_fmt
                self.indent_width = indent_width
                self.indent_first_line = indent_first_line
                # Initialize with the same format as the parent
                super().__init__(fmt=parent_fmt._fmt, datefmt=parent_fmt.datefmt)

            def format(self, record):
                # Get the formatted message from the parent formatter
                formatted_msg = self.parent_formatter.format(record)

                # Split the message into lines
                lines = formatted_msg.splitlines()

                # Create the indentation string
                indent = " " * self.indent_width

                # Apply indentation to lines
                if len(lines) > 0:
                    # Process first line
                    if self.indent_first_line:
                        lines[0] = indent + lines[0]

                    # Process subsequent lines
                    for i in range(1, len(lines)):
                        lines[i] = indent + lines[i]

                # Join the lines back together
                return "\n".join(lines)

        # Return the custom formatter instance
        return IndentedLoggingFormatter(
            parent_formatter, self.indent_width, self.indent_first_line
        )

    def model_post_init(self, *args, **kwargs):
        """
        Post-initialization processing.

        Validates that indent_width is a positive integer.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            ValueError: If indent_width is not a positive integer.
        """
        # Validate indent_width
        if self.indent_width < 0:
            raise ValueError("indent_width must be a positive integer")
