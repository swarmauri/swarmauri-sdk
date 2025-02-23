from abc import ABC, abstractmethod
import logging

class ILoggingHandler(ABC):

    @abstractmethod
    def compile_handler(self) -> logging.Handler:
        """
        Compiles and returns a logging.Handler instance.
        """
        pass