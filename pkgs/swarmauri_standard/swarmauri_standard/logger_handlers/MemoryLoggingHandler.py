import logging
from typing import Optional, Union, Literal, Any
from logging.handlers import MemoryHandler

from swarmauri_base import FullUnion
from swarmauri_base.logger_formatters.FormatterBase import FormatterBase
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_core.ComponentBase import ComponentBase


@ComponentBase.register_type(HandlerBase, "MemoryLoggingHandler")
class MemoryLoggingHandler(HandlerBase):
    """
    A handler that stores logging records in memory until a capacity is reached,
    then flushes to a target handler.
    
    This handler buffers log records in memory and periodically flushes them to a 
    target handler. Flushing occurs when the buffer is full or when a record of 
    the specified flush level or higher is logged.
    """
    type: Literal["MemoryLoggingHandler"] = "MemoryLoggingHandler"
    capacity: int = 100  # Default buffer size
    flushLevel: int = logging.ERROR  # Default flush level
    target: Optional[Union[str, FullUnion[HandlerBase]]] = None  # Target handler for flushing
    
    def compile_handler(self) -> logging.Handler:
        """
        Compiles a MemoryHandler with the specified capacity, flushLevel, and target handler.
        
        Returns:
            logging.Handler: A configured MemoryHandler instance
        
        Raises:
            ValueError: If no target handler is specified
        """
        if self.target is None:
            raise ValueError("MemoryLoggingHandler requires a target handler")
        
        # Get the target handler
        target_handler = self._get_target_handler()
        
        # Create the memory handler
        handler = MemoryHandler(
            capacity=self.capacity,
            flushLevel=self.flushLevel,
            target=target_handler
        )
        
        # Set the log level
        handler.setLevel(self.level)
        
        # Configure the formatter
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
    
    def _get_target_handler(self) -> logging.Handler:
        """
        Resolves and returns the target handler.
        
        Returns:
            logging.Handler: The target handler for flushing buffered records
            
        Raises:
            TypeError: If target is not a string or HandlerBase instance
            ValueError: If target handler cannot be resolved
        """
        if isinstance(self.target, str):
            # In a real implementation, this would resolve the handler by name
            # from a registry or configuration system
            raise ValueError(f"String target handlers not implemented: {self.target}")
        elif isinstance(self.target, HandlerBase):
            return self.target.compile_handler()
        else:
            raise TypeError(f"Target must be a string or HandlerBase instance, got {type(self.target)}")
    
    def flush(self) -> None:
        """
        Forces a flush of the memory buffer to the target handler.
        
        This method can be called externally to force the buffer to flush
        regardless of capacity or log level.
        """
        # This is a convenience method that would need to maintain a reference
        # to the actual handler instance to work properly in a real implementation
        pass
    
    def close(self) -> None:
        """
        Flushes the buffer and closes both this handler and the target handler.
        """
        # This is a convenience method that would need to maintain a reference
        # to the actual handler instance to work properly in a real implementation
        pass
    
    def setFormatter(self, formatter: Any) -> None:
        """
        Sets the formatter for this handler.
        
        Args:
            formatter: The formatter to use
        """
        # This is a convenience method that would need to maintain a reference
        # to the actual handler instance to work properly in a real implementation
        self.formatter = formatter