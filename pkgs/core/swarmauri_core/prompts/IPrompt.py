from abc import ABC, abstractmethod
from typing import Optional, Any

class IPrompt(ABC):
    """
    A base abstract class representing a prompt system.

    Methods:
        __call__: Abstract method that subclasses must implement to enable the instance to be called directly.
    """

    @abstractmethod
    def __call__(self, **kwargs) -> str:
        """
        Abstract method that subclasses must implement to define the behavior of the prompt when called.

        """
        pass
