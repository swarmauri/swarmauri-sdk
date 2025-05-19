import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from typing import Any, Literal, Optional, Union

from swarmauri_base import FullUnion
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_base.ObserveBase import ObserveBase


@ObserveBase.register_model()
class TimedRotatingFileLoggingHandler(HandlerBase):
    """
    A handler that extends FileHandler to rollover log files based on time intervals.

    This handler uses TimedRotatingFileHandler from the standard logging module to
    rotate log files at specified time intervals, such as daily at midnight.

    Attributes
    ----------
    type : Literal["TimedRotatingFileLoggingHandler"]
        The type identifier for this handler
    filename : str
        The path to the log file
    when : str
        The type of interval - 'S' (seconds), 'M' (minutes), 'H' (hours),
        'D' (days), 'W0'-'W6' (weekday, 0=Monday), 'midnight'
    interval : int
        The interval count (e.g., 1 for once per day with when='D')
    backupCount : int
        The number of backup files to keep
    encoding : Optional[str]
        The encoding to use for the log file
    delay : bool
        If True, the file opening is deferred until the first log record is emitted
    utc : bool
        If True, times in UTC will be used; otherwise local time is used
    atTime : Optional[datetime]
        The time of day to rotate (only relevant for 'midnight' or 'W' whens)
    level : int
        The logging level for this handler
    formatter : Optional[Union[str, FullUnion[FormatterBase]]]
        The formatter to use for log messages
    """

    type: Literal["TimedRotatingFileLoggingHandler"] = "TimedRotatingFileLoggingHandler"
    filename: str
    when: str = "midnight"
    interval: int = 1
    backupCount: int = 7
    encoding: Optional[str] = None
    delay: bool = False
    utc: bool = False
    atTime: Optional[datetime] = None
    level: int = logging.INFO
    formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None

    def compile_handler(self) -> logging.Handler:
        """
        Compiles a timed rotating file handler using the specified parameters.

        This method creates a TimedRotatingFileHandler with the configured
        rotation settings, log level, and formatter.

        Returns
        -------
        logging.Handler
            The configured TimedRotatingFileHandler instance
        """
        # Create the timed rotating file handler with the specified parameters
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

        # Set the log level
        handler.setLevel(self.level)

        # Apply formatter if specified, otherwise use a default formatter
        if self.formatter:
            if isinstance(self.formatter, str):
                # If formatter is a string, create a Formatter with the string as format
                handler.setFormatter(logging.Formatter(self.formatter))
            else:
                # If formatter is a FormatterBase instance, compile it
                handler.setFormatter(self.formatter.compile_formatter())
        else:
            # Use default formatter if none specified
            default_formatter = logging.Formatter(
                "[%(asctime)s][%(name)s][%(levelname)s] %(message)s"
            )
            handler.setFormatter(default_formatter)

        return handler

    def get_handler_config(self) -> dict[str, Any]:
        """
        Returns the configuration of this handler as a dictionary.

        This method is useful for serialization or debugging purposes.

        Returns
        -------
        dict[str, Any]
            A dictionary containing the handler's configuration
        """
        return {
            "type": self.type,
            "filename": self.filename,
            "when": self.when,
            "interval": self.interval,
            "backupCount": self.backupCount,
            "encoding": self.encoding,
            "delay": self.delay,
            "utc": self.utc,
            "atTime": self.atTime,
            "level": self.level,
            "formatter": self.formatter,
        }
