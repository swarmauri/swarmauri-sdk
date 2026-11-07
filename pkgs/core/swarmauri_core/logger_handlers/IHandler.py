import logging
from abc import ABC, abstractmethod


class IHandler(ABC):
    @abstractmethod
    def compile_handler(self) -> logging.Handler:
        """
        Compiles and returns a logging.Handler instance.
        """
