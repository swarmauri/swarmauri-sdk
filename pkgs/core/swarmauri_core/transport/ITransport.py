from abc import ABC, abstractmethod
from typing import Any, List


class ITransportComm(ABC):
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

    @abstractmethod
    def subscribe(self, topic: str, subscriber: str) -> None:
        """
        Subscribe to a specific transportation topic
        """
        pass

    @abstractmethod
    def publish(self, topic: str, message: Any) -> None:
        """
        Publish a message to a specific topic
        """
        pass