import logging
from abc import ABC, abstractmethod


class IFormatter(ABC):
    """Interface for logger formatters that define how log messages are
    formatted."""

    @abstractmethod
    def compile_formatter(self) -> logging.Formatter:
        """Create and return a logging.Formatter instance."""
