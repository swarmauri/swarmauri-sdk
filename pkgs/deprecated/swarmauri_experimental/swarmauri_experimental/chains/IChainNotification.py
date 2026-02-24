from abc import ABC, abstractmethod

class IChainNotifier(ABC):
    @abstractmethod
    def send_notification(self, message: str) -> None:
        """Send a notification message based on chain execution results."""
        pass