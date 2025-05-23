from typing import Optional, Union, Literal
import logging
import os
from logging.handlers import RotatingFileHandler

from swarmauri_base import FullUnion
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.ObserveBase import ObserveBase


@ObserveBase.register_model()
class FileLoggingHandler(HandlerBase):
    """
    A handler for logging messages to a file on disk.

    This handler writes logging records to a specified file path using Python's
    built-in FileHandler, managing file operations including opening, writing,
    and closing the file.

    Attributes:
        type: The type identifier for this handler.
        level: The logging level for this handler.
        formatter: Optional formatter for log messages.
        file_path: Path to the log file.
        file_mode: Mode for opening the file ('a' for append, 'w' for write).
        encoding: Character encoding for the file.
        max_bytes: Maximum file size before rotation (0 means no rotation).
        backup_count: Number of backup files to keep when rotating.
    """

    type: Literal["FileLoggingHandler"] = "FileLoggingHandler"
    level: int = logging.INFO
    formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None
    file_path: str = "logs/app.log"
    file_mode: str = "a"
    encoding: str = "utf-8"
    max_bytes: int = 0  # 0 means no rotation
    backup_count: int = 0

    def compile_handler(self) -> logging.Handler:
        """
        Compiles a file logging handler using the specified parameters.

        Creates a FileHandler or RotatingFileHandler based on configuration,
        sets the appropriate logging level and formatter.

        Returns:
            logging.Handler: Configured file handler for logging.

        Raises:
            IOError: If the file path is invalid or inaccessible.
        """
        # Ensure the directory exists
        log_dir = os.path.dirname(self.file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        # Create the appropriate file handler based on rotation settings
        if self.max_bytes > 0:
            # Create a rotating file handler
            handler = RotatingFileHandler(
                filename=self.file_path,
                mode=self.file_mode,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding=self.encoding,
            )
        else:
            # Create a standard file handler
            handler = logging.FileHandler(
                filename=self.file_path, mode=self.file_mode, encoding=self.encoding
            )

        # Set the logging level
        handler.setLevel(self.level)

        # Configure the formatter
        if self.formatter:
            if isinstance(self.formatter, str):
                handler.setFormatter(logging.Formatter(self.formatter))
            else:
                handler.setFormatter(self.formatter.compile_formatter())
        else:
            # Apply default formatter if none is specified
            default_formatter = logging.Formatter(
                "[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
                "%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(default_formatter)

        return handler
