import logging
import os
from typing import Optional, Union, Literal, Dict, Any

from swarmauri_base import FullUnion
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_core.ComponentBase import ComponentBase


@ComponentBase.register_type(HandlerBase, "RotatingFileLoggingHandler")
class RotatingFileLoggingHandler(HandlerBase):
    """
    A logging handler that rotates log files when they reach a certain size.

    This handler extends the base HandlerBase to provide functionality for
    rotating log files once they exceed a specified size, keeping a set number
    of backup files.

    Attributes
    ----------
    type : Literal["RotatingFileLoggingHandler"]
        The type identifier for this handler.
    filename : str
        The path to the log file.
    maxBytes : int
        Maximum file size in bytes before rollover occurs.
    backupCount : int
        Number of backup files to keep.
    encoding : Optional[str]
        Encoding to use for the log file.
    delay : bool
        If True, file opening is deferred until first log record is emitted.
    level : int
        The logging level for this handler.
    formatter : Optional[Union[str, FullUnion[FormatterBase]]]
        The formatter to use for log messages.
    """

    type: Literal["RotatingFileLoggingHandler"] = "RotatingFileLoggingHandler"
    filename: str
    maxBytes: int = 1048576  # Default to 1MB
    backupCount: int = 5
    encoding: Optional[str] = None
    delay: bool = False

    def __init__(self, **data: Any):
        """
        Initialize a new RotatingFileLoggingHandler.

        Parameters
        ----------
        **data : Any
            Keyword arguments for initializing the handler attributes.
        """
        super().__init__(**data)

        # Ensure the directory exists
        if hasattr(self, "filename"):
            directory = os.path.dirname(self.filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

    def compile_handler(self) -> logging.Handler:
        """
        Compile and return a configured RotatingFileHandler.

        This method creates a logging.handlers.RotatingFileHandler with the
        specified parameters and configures it with the appropriate level
        and formatter.

        Returns
        -------
        logging.Handler
            A configured RotatingFileHandler instance.
        """
        from logging.handlers import RotatingFileHandler

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

        # Configure the formatter
        if self.formatter:
            if isinstance(self.formatter, str):
                handler.setFormatter(logging.Formatter(self.formatter))
            else:
                handler.setFormatter(self.formatter.compile_formatter())
        else:
            # Use a default formatter if none is specified
            default_formatter = logging.Formatter(
                "[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
                "%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(default_formatter)

        return handler

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the handler configuration to a dictionary.

        Returns
        -------
        Dict[str, Any]
            Dictionary representation of the handler configuration.
        """
        result = super().to_dict()
        result.update(
            {
                "filename": self.filename,
                "maxBytes": self.maxBytes,
                "backupCount": self.backupCount,
            }
        )

        if self.encoding:
            result["encoding"] = self.encoding

        if self.delay:
            result["delay"] = self.delay

        return result
