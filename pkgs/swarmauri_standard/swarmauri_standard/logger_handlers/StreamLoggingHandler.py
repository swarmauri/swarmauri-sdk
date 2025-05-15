import logging
import sys
from typing import Any, Literal, Optional, TextIO, Union

from swarmauri_base import FullUnion
from swarmauri_base.ObserveBase import ObserveBase
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase


@ObserveBase.register_model()
class StreamLoggingHandler(HandlerBase):
    """
    A logging handler that writes log records to a stream (such as sys.stdout or sys.stderr).
    This handler uses Python's built-in StreamHandler to output logs to the specified stream.

    Attributes
    ----------
    type : Literal["StreamLoggingHandler"]
        The type identifier for this handler.
    level : int
        The logging level for this handler.
    formatter : Optional[Union[str, FullUnion[FormatterBase]]]
        The formatter to use for formatting log records.
    stream : Optional[TextIO]
        The stream to which log records will be written. Defaults to sys.stderr.
    """

    type: Literal["StreamLoggingHandler"] = "StreamLoggingHandler"
    level: int = logging.INFO
    formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None
    stream: Optional[TextIO] = None

    def __init__(
        self,
        level: int = logging.INFO,
        formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None,
        stream: Optional[TextIO] = None,
        **kwargs: Any,
    ):
        """
        Initialize a new StreamLoggingHandler.

        Parameters
        ----------
        level : int, optional
            The logging level for this handler, by default logging.INFO
        formatter : Optional[Union[str, FullUnion[FormatterBase]]], optional
            The formatter to use for formatting log records, by default None
        stream : Optional[TextIO], optional
            The stream to which log records will be written, by default None
            If not specified, sys.stderr will be used.
        **kwargs : Any
            Additional keyword arguments passed to the parent class.
        """
        super().__init__(level=level, formatter=formatter, **kwargs)
        self.stream = stream

    def compile_handler(self) -> logging.Handler:
        """
        Compiles a logging.StreamHandler with the configured level, formatter, and stream.

        Returns
        -------
        logging.Handler
            A configured StreamHandler instance ready for use.
        """
        # Create a StreamHandler with the specified stream or default to sys.stderr
        handler = logging.StreamHandler(self.stream if self.stream else sys.stderr)

        # Set the log level
        handler.setLevel(self.level)

        # Configure the formatter
        if self.formatter:
            if isinstance(self.formatter, str):
                # If formatter is a string, create a Formatter with that format string
                handler.setFormatter(logging.Formatter(self.formatter))
            else:
                # If formatter is a FormatterBase instance, compile it
                handler.setFormatter(self.formatter.compile_formatter())
        else:
            # Use a default formatter if none is specified
            default_formatter = logging.Formatter(
                "[%(name)s][%(levelname)s] %(message)s"
            )
            handler.setFormatter(default_formatter)

        return handler
