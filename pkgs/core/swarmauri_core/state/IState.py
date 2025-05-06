from abc import ABC, abstractmethod
from typing import Dict, Any


class IState(ABC):
    @abstractmethod
    def read(self) -> Dict[str, Any]:
        """
        Reads and returns the current state as a dictionary.
        """

    @abstractmethod
    def write(self, data: Dict[str, Any]) -> None:
        """
        Replaces the current state with the given data.
        """

    @abstractmethod
    def update(self, data: Dict[str, Any]) -> None:
        """
        Updates the state with the given data.
        """

    @abstractmethod
    def reset(self) -> None:
        """
        Resets the state to its initial state.
        """
