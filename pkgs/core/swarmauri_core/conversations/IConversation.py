from abc import ABC, abstractmethod

from swarmauri_core.messages.IMessage import IMessage


class IConversation(ABC):
    """
    Interface for managing conversations, defining abstract methods for
    adding messages, retrieving the latest message, getting all messages, and
    clearing history.
    """

    @property
    def history(self) -> list[IMessage]:
        """
        Provides read-only access to the conversation history.
        """

    @abstractmethod
    def add_message(self, message: IMessage):
        """
        Adds a message to the conversation history.
        """

    @abstractmethod
    def add_messages(self, messages: list[IMessage]):
        """
        Adds multiple messages to the conversation history.
        """

    @abstractmethod
    def get_last(self) -> IMessage | None:
        """
        Retrieves the latest message from the conversation history.
        """

    @abstractmethod
    def clear_history(self) -> None:
        """
        Clears the conversation history.
        """
