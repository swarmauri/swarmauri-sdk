import logging
import queue
from logging.handlers import QueueHandler
from typing import Any, Literal, Optional, Union

from pydantic import Field
from swarmauri_base import FullUnion
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_base.ObserveBase import ObserveBase


@ObserveBase.register_model()
class QueueLoggingHandler(HandlerBase):
    """
    A logging handler that puts log records onto a queue for asynchronous processing.

    This handler uses Python's QueueHandler to enqueue log records for processing by a
    separate listener thread, allowing the logging operation to be non-blocking.

    Attributes:
        type: The type identifier for this handler.
        queue: The queue instance where log records will be placed.
        level: The logging level for this handler.
        formatter: Optional formatter for formatting log records.
        respect_handler_level: Whether to respect the handler's level when enqueuing records.
    """

    type: Literal["QueueLoggingHandler"] = "QueueLoggingHandler"
    queue: Any = Field(default_factory=queue.Queue, exclude=True)
    level: int = logging.INFO
    formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None
    respect_handler_level: bool = True

    def compile_handler(self) -> logging.Handler:
        """
        Compiles a QueueHandler using the specified queue, level, and formatter.

        Returns:
            logging.Handler: A configured QueueHandler instance.
        """
        # Create a QueueHandler with the specified queue
        handler = QueueHandler(self.queue)
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
                "[%(name)s][%(levelname)s] %(message)s"
            )
            handler.setFormatter(default_formatter)

        # Configure the handler to respect level or not
        handler.respect_handler_level = self.respect_handler_level

        return handler

    def get_queue(self) -> Any:
        """
        Get the queue used by this handler.

        This is useful when setting up a QueueListener to process the log records.

        Returns:
            Any: The queue instance used by this handler.
        """
        return self.queue

    def set_queue(self, new_queue: Any) -> None:
        """
        Set a new queue for this handler.

        Args:
            new_queue: A queue-like object with a put() method.
        """
        self.queue = new_queue
