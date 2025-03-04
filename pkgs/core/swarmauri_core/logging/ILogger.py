from abc import ABC, abstractmethod
import logging


class ILogger(ABC):
    @abstractmethod
    def compile_logger(self, logger_name: str = __name__) -> logging.Logger:
        """
        Compiles and returns a logging.Logger instance.
        """
        pass
