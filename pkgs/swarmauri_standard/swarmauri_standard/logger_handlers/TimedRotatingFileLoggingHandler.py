import logging
import os
from typing import Literal, Optional, Union, Any
from logging.handlers import TimedRotatingFileHandler

from swarmauri_base import FullUnion
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_core.ComponentBase import ComponentBase


@ComponentBase.register_type(HandlerBase, "TimedRotatingFileLoggingHandler")
class TimedRotatingFileLoggingHandler(HandlerBase):
    """
    A handler that extends FileHandler to rollover log files based on time intervals.

    This handler rotates the log file at certain timed intervals using Python's built-in
    TimedRotatingFileHandler. For example, you can set it to rotate logs daily at midnight,
    hourly, or at any other time interval.

    Attributes
    ----------
    type : Literal["TimedRotatingFileLoggingHandler"]
        The type identifier for this handler.
    level : int
        The logging level for this handler.
    formatter : Optional[Union[str, FullUnion[FormatterBase]]]
        The formatter to use for formatting log records.
    filename : str
        Path to the log file.
    when : str
        Specifies the type of interval. Can be one of 'S' (seconds), 'M' (minutes),
        'H' (hours), 'D' (days), 'W0'-'W6' (weekday, 0=Monday), 'midnight'.
    interval : int
        The interval value according to the when parameter.
    backupCount : int
        The number of backup files to keep.
    encoding : Optional[str]
        The encoding to use for the log file.
    delay : bool
        If True, the file will not be created until the first log record is emitted.
    utc : bool
        If True, times in UTC will be used; otherwise local time is used.
    atTime : Optional[Any]
        The time of day when rollover occurs, for 'midnight' or 'W0'-'W6'.
    """

    type: Literal["TimedRotatingFileLoggingHandler"] = "TimedRotatingFileLoggingHandler"
    level: int = logging.INFO
    formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None
    filename: str = "app.log"
    when: str = "midnight"
    interval: int = 1
    backupCount: int = 7
    encoding: Optional[str] = None
    delay: bool = False
    utc: bool = False
    atTime: Optional[Any] = None

    def compile_handler(self) -> logging.Handler:
        """
        Compiles a TimedRotatingFileHandler using the specified configuration.

        This method creates a new TimedRotatingFileHandler instance with the configured
        parameters, sets the appropriate logging level, and applies the formatter.

        Returns
        -------
        logging.Handler
            A configured TimedRotatingFileHandler instance.
        """
        # Ensure the directory exists
        log_dir = os.path.dirname(self.filename)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Create the timed rotating file handler
        handler = TimedRotatingFileHandler(
            filename=self.filename,
            when=self.when,
            interval=self.interval,
            backupCount=self.backupCount,
            encoding=self.encoding,
            delay=self.delay,
            utc=self.utc,
            atTime=self.atTime,
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
            # Use a default formatter if none is specified
            default_formatter = logging.Formatter(
                "[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
                "%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(default_formatter)

        return handler
