from abc import ABC, abstractmethod
import logging


class IFormatter(ABC):
    """Interface for logger formatters that define how log messages are formatted."""

    @abstractmethod
    def compile_formatter(self) -> logging.Formatter:
        """Create and return a logging.Formatter instance."""
        pass
