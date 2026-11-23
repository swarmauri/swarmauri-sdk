from abc import ABC, abstractmethod
from typing import Any


class IPublish(ABC):
    """Interface defining the contract for publishing messages."""

    @abstractmethod
    def publish(self, channel: str, payload: dict[str, Any]) -> None:
        """Publish ``payload`` to ``channel``."""
