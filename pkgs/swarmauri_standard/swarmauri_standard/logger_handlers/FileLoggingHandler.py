from logging.handlers import RotatingFileHandler
import logging
import os
from typing import Optional, Literal, Dict, Any

from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_core.ComponentBase import ComponentBase


@ComponentBase.register_type(HandlerBase, "FileLoggingHandler")
class FileLoggingHandler(HandlerBase):
    """
    A handler that writes logging records to a specified file path.

    This handler extends the base HandlerBase class to provide file-based logging
    functionality. It uses Python's built-in FileHandler to manage writing logs
    to disk, handling file opening, closing, and various file modes.
    """

    type: Literal["FileLoggingHandler"] = "FileLoggingHandler"

    # File configuration
    filepath: str
    mode: str = "a"  # Default to append mode
    encoding: Optional[str] = "utf-8"
    delay: bool = False  # Don't delay file creation

    # Rotation settings (optional)
    max_bytes: int = 0  # 0 means no rotation
    backup_count: int = 0  # 0 means no backups

    def __init__(self, **data: Any):
        """
        Initialize the FileLoggingHandler with the provided configuration.

        Args:
            **data: Dictionary containing configuration parameters.
        """
        super().__init__(**data)

        # Ensure the directory exists
        if self.filepath:
            directory = os.path.dirname(self.filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

    def compile_handler(self) -> logging.Handler:
        """
        Compiles a file logging handler using the specified configuration.

        Returns:
            logging.Handler: Configured file handler for logging.
        """
        # Ensure directory exists for the log file
        directory = os.path.dirname(self.filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        # Create the appropriate handler based on rotation settings
        if self.max_bytes > 0:
            # Use RotatingFileHandler if max_bytes is specified
            handler = RotatingFileHandler(
                filename=self.filepath,
                mode=self.mode,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding=self.encoding,
                delay=self.delay,
            )
        else:
            # Use standard FileHandler
            handler = logging.FileHandler(
                filename=self.filepath,
                mode=self.mode,
                encoding=self.encoding,
                delay=self.delay,
            )

        # Set the log level
        handler.setLevel(self.level)

        # Configure formatter
        if self.formatter:
            if isinstance(self.formatter, str):
                handler.setFormatter(logging.Formatter(self.formatter))
            else:
                handler.setFormatter(self.formatter.compile_formatter())
        else:
            # Default formatter if none specified
            default_formatter = logging.Formatter(
                "[%(asctime)s][%(name)s][%(levelname)s] %(message)s"
            )
            handler.setFormatter(default_formatter)

        return handler

    def get_config(self) -> Dict[str, Any]:
        """
        Get the configuration of this handler.

        Returns:
            Dict[str, Any]: Dictionary containing the handler's configuration.
        """
        config = super().get_config() if hasattr(super(), "get_config") else {}
        config.update(
            {
                "type": self.type,
                "filepath": self.filepath,
                "mode": self.mode,
                "encoding": self.encoding,
                "delay": self.delay,
                "max_bytes": self.max_bytes,
                "backup_count": self.backup_count,
                "level": self.level,
            }
        )

        if self.formatter:
            if isinstance(self.formatter, str):
                config["formatter"] = self.formatter
            else:
                config["formatter"] = self.formatter.get_config()

        return config
