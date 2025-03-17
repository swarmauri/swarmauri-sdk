from abc import ABC, abstractmethod
import logging


class IHandler(ABC):
    @abstractmethod
    def compile_handler(self) -> logging.Handler:
        """
        Compiles and returns a logging.Handler instance.
        """
        pass
