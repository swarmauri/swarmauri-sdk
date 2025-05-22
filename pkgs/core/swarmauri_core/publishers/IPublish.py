from abc import ABC, abstractmethod
from typing import Any, Dict


class IPublish(ABC):
    """Interface defining the contract for publishing messages."""

    @abstractmethod
    def publish(self, channel: str, payload: Dict[str, Any]) -> None:
        """Publish ``payload`` to ``channel``."""
        pass
