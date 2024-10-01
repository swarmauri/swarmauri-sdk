from abc import ABC, abstractmethod
from typing import List, Optional
from swarmauri_core.messages.IMessage import IMessage


class IConversation(ABC):
    """
    Interface for managing conversations, defining abstract methods for
    adding messages, retrieving the latest message, getting all messages, and clearing history.
    """

    @property
    def history(self) -> List[IMessage]:
        """
        Provides read-only access to the conversation history.
        """
        pass

    @abstractmethod
    def add_message(self, message: IMessage):
        """
        Adds a message to the conversation history.
        """
        pass

    @abstractmethod
    def add_messages(self, messages: List[IMessage]):
        """
        Adds multiple messages to the conversation history.
        """
        pass

    @abstractmethod
    def get_last(self) -> Optional[IMessage]:
        """
        Retrieves the latest message from the conversation history.
        """
        pass

    @abstractmethod
    def clear_history(self) -> None:
        """
        Clears the conversation history.
        """
        pass
