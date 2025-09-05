import logging

from swarmauri_base import register_type
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase


@register_type()
class BorderFormatter(FormatterBase):
    """
    A formatter that surrounds log messages with borders for visual emphasis.

    This formatter adds configurable border lines above and below messages,
    with options for border character, width, and padding.
    """

    # Border configuration
    border_char: str = "-"
    border_width: int = 80
    padding: int = 1
    message_format: str = None

    def model_post_init(self, *args, **kwargs):
        """
        Initialize the formatter after model creation.

        This method is called after the model is created and sets up the
        formatting string with the border configuration.
        """
        super().model_post_init(*args, **kwargs)
        # Keep the original format to be used inside the border
        self.message_format = self.format

    def compile_formatter(self) -> logging.Formatter:
        """
        Create and return a custom logging.Formatter with border decoration.

        Returns:
            logging.Formatter: A formatter that adds borders to log messages
        """
        original_formatter = logging.Formatter(self.message_format, self.date_format)

        # Create a custom formatter that wraps the original formatter's output with borders
        class BorderedFormatter(logging.Formatter):
            def __init__(self, parent_formatter, border_formatter):
                super().__init__()
                self.parent_formatter = parent_formatter
                self.border_formatter = border_formatter

            def format(self, record):
                # Get the formatted message from the original formatter
                formatted_message = self.parent_formatter.format(record)

                # Apply the border to the formatted message
                return self.border_formatter._apply_border(formatted_message)

        return BorderedFormatter(original_formatter, self)

    def _apply_border(self, message: str) -> str:
        """
        Apply borders to a message.

        Args:
            message: The message to surround with borders

        Returns:
            str: The message with borders applied
        """
        # Create the border line
        border_line = self.border_char * self.border_width

        # Split the message into lines
        message_lines = message.split("\n")

        # Create the bordered message
        bordered_message = []

        # Add top border
        bordered_message.append(border_line)

        # Add padding before message if needed
        if self.padding > 0:
            for _ in range(self.padding):
                bordered_message.append("")

        # Add each line of the message
        for line in message_lines:
            bordered_message.append(line)

        # Add padding after message if needed
        if self.padding > 0:
            for _ in range(self.padding):
                bordered_message.append("")

        # Add bottom border
        bordered_message.append(border_line)

        # Join all lines with newlines
        return "\n".join(bordered_message)

    def set_border_style(
        self, char: str = "-", width: int = 80, padding: int = 1
    ) -> None:
        """
        Update the border style configuration.

        Args:
            char: The character to use for the border
            width: The width of the border
            padding: Number of empty lines between border and message
        """
        self.border_char = char
        self.border_width = width
        self.padding = padding
