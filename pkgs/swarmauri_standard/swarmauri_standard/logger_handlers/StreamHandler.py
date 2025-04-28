"""
StreamHandler.py

This module provides a logging handler that outputs to standard output streams.
It extends HandlerBase and provides configurable options for stream output,
including the ability to specify different output streams (stdout, stderr).
"""

import logging
import sys
from enum import Enum
from typing import Literal

from pydantic import Field
from swarmauri_base.logger_handler.HandlerBase import HandlerBase
from swarmauri_base.ObserveBase import ObserveBase


class StreamType(str, Enum):
    """Enumeration of available output streams."""

    STDOUT = "stdout"
    STDERR = "stderr"


@ObserveBase.register_type(HandlerBase, "StreamHandler")
class StreamHandler(HandlerBase):
    """
    A handler for routing log messages to a specified output stream (stdout/stderr).

    This handler extends HandlerBase and specializes in streaming log output to
    standard output channels. It allows for customization of stream target,
    log level, and formatting.

    Attributes:
        stream_type (StreamType): The type of stream to use (stdout or stderr).
        level (int): The logging level threshold.
        formatter (Optional[Union[str, FormatterBase]]): Formatter for log messages.
        colorize (bool): Whether to colorize output based on level.
    """

    type: Literal["StreamHandler"] = "StreamHandler"
    stream_type: StreamType = Field(
        default=StreamType.STDOUT, description="The stream to write logs to"
    )
    colorize: bool = Field(
        default=False, description="Whether to colorize log output based on level"
    )

    def compile_handler(self) -> logging.Handler:
        """
        Compiles a logging handler that outputs to the specified stream.

        Returns:
            logging.Handler: A configured logging.StreamHandler instance.
        """
        # Select the appropriate stream based on stream_type
        if self.stream_type == StreamType.STDERR:
            stream = sys.stderr
        else:
            stream = sys.stdout

        # Create a stream handler with the specified stream
        handler = logging.StreamHandler(stream)
        handler.setLevel(self.level)

        # Configure the formatter
        if self.formatter:
            if isinstance(self.formatter, str):
                handler.setFormatter(logging.Formatter(self.formatter))
            else:
                handler.setFormatter(self.formatter.compile_formatter())
        else:
            if self.colorize:
                formatter = self._get_colorized_formatter()
            else:
                formatter = logging.Formatter("[%(name)s][%(levelname)s] %(message)s")
            handler.setFormatter(formatter)

        return handler

    def _get_colorized_formatter(self) -> logging.Formatter:
        """
        Creates a formatter that colorizes log messages based on their level.

        Returns:
            logging.Formatter: A formatter with colorized output.
        """
        # ANSI color codes
        RESET = "\033[0m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RED = "\033[31m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"

        # Format with color based on log level
        class ColorFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                # Select color based on level
                if record.levelno >= logging.CRITICAL:
                    color = MAGENTA
                elif record.levelno >= logging.ERROR:
                    color = RED
                elif record.levelno >= logging.WARNING:
                    color = YELLOW
                elif record.levelno >= logging.INFO:
                    color = GREEN
                else:
                    color = BLUE

                levelname = f"{color}[{record.levelname}]{RESET}"
                return f"[{record.name}]{levelname} {record.getMessage()}"

        return ColorFormatter()

    def __repr__(self) -> str:
        """String representation of the StreamHandler."""
        return f"StreamHandler(stream={self.stream_type.value}, level={logging.getLevelName(self.level)})"
