import logging
from typing import ClassVar, Dict

from swarmauri_base import register_type
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase


@register_type()
class ColorFormatter(FormatterBase):
    """
    A formatter that adds ANSI color codes to log messages based on log level.

    This formatter enhances log readability by color-coding different log levels
    without requiring external dependencies. It's implemented in pure Python using
    ANSI escape sequences.
    """

    # Color codes for different log levels
    COLORS: ClassVar[Dict[str, str]] = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[41m",  # Red background
    }
    RESET: ClassVar[str] = "\033[0m"  # Reset ANSI color codes

    format: str = "[%(name)s][%(levelname)s] %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    use_colors: bool = True
    include_timestamp: bool = False
    include_process: bool = False
    include_thread: bool = False

    def model_post_init(self, *args, **kwargs):
        """
        Initialize the formatter with the specified format string.

        This method is called after the model is initialized and sets up the
        format string based on the configuration options.
        """
        format_parts = []

        if self.include_timestamp:
            format_parts.append("%(asctime)s")

        format_parts.append("[%(name)s]")
        format_parts.append("[%(levelname)s]")

        if self.include_process:
            format_parts.append("Process:%(process)d")

        if self.include_thread:
            format_parts.append("Thread:%(thread)d")

        format_parts.append("%(message)s")

        self.format = " ".join(format_parts)

    def compile_formatter(self) -> logging.Formatter:
        """
        Create and return a custom logging.Formatter that applies color codes.

        Returns:
            logging.Formatter: A formatter instance that adds color to log messages
                               based on their level when use_colors is True.
        """
        if not self.use_colors:
            # If colors are disabled, use the parent class implementation
            return super().compile_formatter()

        # Create a custom formatter class that adds color codes
        class ColoredFormatter(logging.Formatter):
            def __init__(self, fmt, datefmt, colors, reset):
                super().__init__(fmt, datefmt)
                self.colors = colors
                self.reset = reset

            def format(self, record):
                # Save the original levelname
                orig_levelname = record.levelname

                # Add color codes to the levelname if the level has a defined color
                if record.levelname in self.colors:
                    # Prepend color code to levelname and append reset code
                    record.levelname = (
                        f"{self.colors[record.levelname]}{record.levelname}{self.reset}"
                    )

                # Format the record
                result = super().format(record)

                # Restore the original levelname for potential reuse
                record.levelname = orig_levelname

                return result

        # Return an instance of our custom formatter
        return ColoredFormatter(self.format, self.date_format, self.COLORS, self.RESET)

    def disable_colors(self) -> None:
        """
        Disable color output in log messages.

        This method allows for runtime control of color formatting.
        """
        self.use_colors = False

    def enable_colors(self) -> None:
        """
        Enable color output in log messages.

        This method allows for runtime control of color formatting.
        """
        self.use_colors = True

    def is_using_colors(self) -> bool:
        """
        Check if color formatting is currently enabled.

        Returns:
            bool: True if color formatting is enabled, False otherwise.
        """
        return self.use_colors
