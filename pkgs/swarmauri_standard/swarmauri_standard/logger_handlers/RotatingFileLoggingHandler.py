from typing import Literal, Optional, Union
import logging
from logging.handlers import RotatingFileHandler
import os

from swarmauri_base.ObserveBase import ObserveBase
from swarmauri_base import FullUnion
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase


@ObserveBase.register_model()
class RotatingFileLoggingHandler(HandlerBase):
    """
    A handler that rotates log files when they reach a specified size.

    This handler extends the base HandlerBase to provide log file rotation functionality.
    When the log file reaches the specified maxBytes, it is rotated and a new file is created.
    The handler keeps a specified number of backup files.

    Attributes
    ----------
    type : Literal["RotatingFileLoggingHandler"]
        The type identifier for this handler.
    level : int
        The logging level for this handler.
    formatter : Optional[Union[str, FullUnion[FormatterBase]]]
        The formatter to use for this handler.
    filename : str
        The name of the log file.
    maxBytes : int
        The maximum size in bytes before the log file is rotated.
    backupCount : int
        The number of backup files to keep.
    encoding : Optional[str]
        The encoding to use for the log file.
    delay : bool
        If True, the file opening is deferred until the first log record is emitted.
    """

    type: Literal["RotatingFileLoggingHandler"] = "RotatingFileLoggingHandler"
    level: int = logging.INFO
    formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None
    filename: str = "app.log"
    maxBytes: int = 10485760  # 10 MB default
    backupCount: int = 5
    encoding: Optional[str] = None
    delay: bool = False

    def compile_handler(self) -> logging.Handler:
        """
        Compiles a rotating file logging handler using the specified parameters.

        This method creates a RotatingFileHandler with the specified filename, maximum bytes,
        backup count, and other parameters. It also sets the logging level and formatter.

        Returns
        -------
        logging.Handler
            A configured RotatingFileHandler instance.
        """
        # Ensure the directory exists
        log_dir = os.path.dirname(self.filename)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        # Create the rotating file handler
        handler = RotatingFileHandler(
            filename=self.filename,
            maxBytes=self.maxBytes,
            backupCount=self.backupCount,
            encoding=self.encoding,
            delay=self.delay,
        )

        # Set the logging level
        handler.setLevel(self.level)
        # Apply formatter
        if self.formatter:
            if isinstance(self.formatter, str):
                handler.setFormatter(logging.Formatter(self.formatter))
            else:
                handler.setFormatter(self.formatter.compile_formatter())
        else:
            # Default formatter if none is specified
            default_formatter = logging.Formatter(
                "[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(default_formatter)

        return handler
