from queue import Queue
import logging
from typing import Optional, Union, Literal, Any

from swarmauri_base import FullUnion
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_core.ComponentBase import ComponentBase


@ComponentBase.register_type(HandlerBase, "QueueLoggingHandler")
class QueueLoggingHandler(HandlerBase):
    """
    A handler that puts logging records onto a queue for processing by a listener.
    
    This handler is designed to be used with QueueListener for asynchronous logging.
    It allows log records to be processed in a separate thread or process, which can
    prevent logging from blocking the main application.
    """
    type: Literal["QueueLoggingHandler"] = "QueueLoggingHandler"
    queue: Optional[Queue] = None
    respect_handler_level: bool = True
    
    def __init__(
        self, 
        queue: Optional[Queue] = None, 
        level: int = logging.INFO,
        formatter: Optional[Union[str, FullUnion[FormatterBase]]] = None,
        respect_handler_level: bool = True
    ):
        """
        Initialize the QueueLoggingHandler.
        
        Args:
            queue: The queue to use for logging records. Must support put() method.
            level: The logging level to use for this handler.
            formatter: The formatter to use for formatting log messages.
            respect_handler_level: Whether to respect the handler's level when processing records.
        """
        super().__init__(level=level, formatter=formatter)
        self.queue = queue if queue is not None else Queue()
        self.respect_handler_level = respect_handler_level
    
    def compile_handler(self) -> logging.Handler:
        """
        Compile and return a QueueHandler instance for logging.
        
        Returns:
            A configured QueueHandler instance.
        """
        # Create a custom QueueHandler that respects our configuration
        class CustomQueueHandler(logging.handlers.QueueHandler):
            def __init__(self, queue, respect_handler_level, parent_handler):
                super().__init__(queue)
                self.respect_handler_level = respect_handler_level
                self.parent_handler = parent_handler
            
            def emit(self, record):
                # Respect the handler level if configured to do so
                if self.respect_handler_level and not self.filter(record):
                    return
                # Use the standard queue handler emit logic
                super().emit(record)
        
        # Import here to avoid circular imports
        from logging.handlers import QueueHandler
        
        # Create and configure the handler
        handler = CustomQueueHandler(
            self.queue, 
            self.respect_handler_level,
            self
        )
        handler.setLevel(self.level)
        
        # Set the formatter
        if self.formatter:
            if isinstance(self.formatter, str):
                handler.setFormatter(logging.Formatter(self.formatter))
            else:
                handler.setFormatter(self.formatter.compile_formatter())
        else:
            default_formatter = logging.Formatter(
                "[%(name)s][%(levelname)s] %(message)s"
            )
            handler.setFormatter(default_formatter)
        
        return handler
    
    def prepare_queue_listener(self, handlers: list[logging.Handler]) -> Any:
        """
        Create and return a QueueListener for processing log records.
        
        Args:
            handlers: List of handlers to process the log records.
            
        Returns:
            A configured QueueListener instance.
        """
        # Import here to avoid circular imports
        from logging.handlers import QueueListener
        
        # Create and return a queue listener
        return QueueListener(self.queue, *handlers, respect_handler_level=self.respect_handler_level)
    
    def get_queue(self) -> Queue:
        """
        Get the queue used by this handler.
        
        Returns:
            The queue instance.
        """
        return self.queue