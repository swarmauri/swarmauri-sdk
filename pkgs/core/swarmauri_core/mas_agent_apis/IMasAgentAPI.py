from abc import ABC, abstractmethod
from typing import Any


class IMasAgentAPI(ABC):
    """Interface for MAS-specific agent-local APIs."""

    @abstractmethod
    def send_message(self, message: Any) -> None:
        """Send a message to the MAS agent."""
        pass

    @abstractmethod
    def subscribe(self, topic: str) -> None:
        """Subscribe to a topic."""
        pass

    @abstractmethod
    def publish(self, topic: str) -> None:
        """Publish a message to a topic."""
        pass
