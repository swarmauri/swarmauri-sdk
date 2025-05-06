from abc import ABC, abstractmethod
from typing import Any, List


class ITransport(ABC):
    """
    Interface defining standard transportation methods for agent interactions
    """

    @abstractmethod
    def send(self, sender: str, recipient: str, message: Any) -> None:
        """
        Send a message to a specific recipient
        """
        pass

    @abstractmethod
    def broadcast(self, sender: str, message: Any) -> None:
        """
        Broadcast a message to all agents
        """
        pass

    @abstractmethod
    def multicast(self, sender: str, recipients: List[str], message: Any) -> None:
        """
        Send a message to multiple specific recipients
        """
        pass
