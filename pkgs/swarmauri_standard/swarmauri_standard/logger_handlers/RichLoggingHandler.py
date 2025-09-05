import logging
import os
from typing import Any, Dict, Literal, Optional, Union

from rich.console import Console
from rich.logging import RichHandler
from swarmauri_base import FullUnion
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_base.ObserveBase import ObserveBase


@ObserveBase.register_model()
class RichLoggingHandler(HandlerBase):
    """
    A handler that uses RichHandler from the rich library to output colorized,
    formatted log records to the console or file.

    Attributes
    ----------
    level : int
        The logging level for this handler (default: logging.INFO)
    formatter : Optional[Union[str, FullUnion[FormatterBase]]]
        The formatter to use for formatting log records
    show_time : bool
        Whether to show timestamps in the log output
    show_path : bool
        Whether to show file paths in the log output
    show_level : bool
        Whether to show log levels in the output
    rich_tracebacks : bool
        Whether to use rich tracebacks for exceptions
    console_kwargs : Dict[str, Any]
        Additional keyword arguments to pass to the Rich Console
    enable_markup : bool
        Whether to enable Rich markup in log messages
    log_file_path : Optional[str]
        Path to a file where logs should be written (None for console only)
    """

    type: Literal["RichLoggingHandler"] = "RichLoggingHandler"
    level: int = logging.INFO
    formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None
    show_time: bool = True
    show_path: bool = False
    show_level: bool = True
    rich_tracebacks: bool = True
    console_kwargs: Dict[str, Any] = {}
    enable_markup: bool = True
    log_file_path: Optional[str] = None

    def compile_handler(self) -> logging.Handler:
        """
        Compiles a RichHandler instance configured with the specified settings.

        Returns
        -------
        logging.Handler
            A configured RichHandler instance
        """
        # Set up the Rich console with custom theme if needed
        console_kwargs = self.console_kwargs.copy() if self.console_kwargs else {}

        # If a log file is specified, configure the console to write to that file
        if self.log_file_path:
            # Ensure the directory exists
            log_dir = os.path.dirname(self.log_file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # Create a file for the console to write to
            console_kwargs["file"] = open(self.log_file_path, "a", encoding="utf-8")

        # Create the console with the specified settings
        console = Console(**console_kwargs)

        # Create the RichHandler with our configuration
        handler = RichHandler(
            level=self.level,
            console=console,
            show_time=self.show_time,
            show_path=self.show_path,
            show_level=self.show_level,
            rich_tracebacks=self.rich_tracebacks,
            markup=self.enable_markup,
        )

        # Apply formatter if provided
        if self.formatter:
            if isinstance(self.formatter, str):
                handler.setFormatter(logging.Formatter(self.formatter))
            else:
                handler.setFormatter(self.formatter.compile_formatter())

        return handler
