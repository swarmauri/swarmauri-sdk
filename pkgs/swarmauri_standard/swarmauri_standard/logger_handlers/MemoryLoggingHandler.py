import logging
from logging.handlers import MemoryHandler
from typing import Any, Dict, Literal, Optional, Union

from swarmauri_base import FullUnion
from swarmauri_base.logger_handlers.HandlerBase import HandlerBase
from swarmauri_base.ObserveBase import ObserveBase


@ObserveBase.register_model()
class MemoryLoggingHandler(HandlerBase):
    """
    A handler that stores logging records in memory until a capacity is reached,
    then flushes to a target handler.

    This handler buffers log records in memory and flushes them to a target
    handler when the buffer is full or when a record with a level greater than
    or equal to flushLevel is seen.
    """

    type: Literal["MemoryLoggingHandler"] = "MemoryLoggingHandler"
    capacity: int = 100  # Default buffer size
    flushLevel: int = logging.ERROR  # Default flush level
    target: Optional[Union[str, FullUnion[HandlerBase]]] = None

    def __init__(self, **data: Any):
        """
        Initialize the MemoryLoggingHandler with the provided configuration.

        Args:
            **data: Configuration options for the handler.
        """
        super().__init__(**data)
        self._memory_handler = None
        self._target_handler = None

    def compile_handler(self) -> logging.Handler:
        """
        Compiles a memory logging handler using the specified capacity,
        flushLevel, and target handler.

        Returns:
            logging.Handler: The configured memory handler.

        Raises:
            ValueError: If no target handler is specified.
        """
        if not self.target:
            raise ValueError(
                "MemoryLoggingHandler requires a target handler for flushing records"
            )

        # Resolve the target handler
        if isinstance(self.target, str):
            # This is a placeholder for resolving handler by name
            # In a real implementation, you would look up the handler by name
            raise ValueError(
                f"Target handler resolution by name '{self.target}' not implemented"
            )
        else:
            self._target_handler = self.target.compile_handler()

        # Create the memory handler with the target
        self._memory_handler = MemoryHandler(
            capacity=self.capacity,
            flushLevel=self.flushLevel,
            target=self._target_handler,
        )
        self._memory_handler.setLevel(self.level)

        # Set formatter if provided
        if self.formatter:
            if isinstance(self.formatter, str):
                self._memory_handler.setFormatter(logging.Formatter(self.formatter))
            else:
                self._memory_handler.setFormatter(self.formatter.compile_formatter())
        else:
            default_formatter = logging.Formatter(
                "[%(name)s][%(levelname)s] %(message)s"
            )
            self._memory_handler.setFormatter(default_formatter)

        return self._memory_handler

    def flush(self) -> None:
        """
        Manually flush all buffered log records to the target handler.
        """
        if self._memory_handler:
            self._memory_handler.flush()

    def close(self) -> None:
        """
        Close the memory handler and its target handler.
        """
        if self._memory_handler:
            self._memory_handler.close()
        if self._target_handler:
            self._target_handler.close()

    def setTarget(self, target_handler: logging.Handler) -> None:
        """
        Set a new target handler for this memory handler.

        Args:
            target_handler: The new target handler to use for flushing.
        """
        if self._memory_handler:
            self._memory_handler.setTarget(target_handler)
        self._target_handler = target_handler

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the handler configuration to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the handler.
        """
        # Start with base attributes
        result = {
            "type": self.type,
            "level": self.level,
            "formatter": str(self.formatter) if self.formatter else None,
        }

        # Add MemoryLoggingHandler specific attributes
        result.update(
            {
                "capacity": self.capacity,
                "flushLevel": self.flushLevel,
                "target": self.target.to_dict()
                if hasattr(self.target, "to_dict")
                else self.target,
            }
        )
        return result
