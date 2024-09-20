from abc import ABC, abstractmethod
from typing import Callable, Dict, Union
from ...core.messages.IMessage import IMessage
from ...core.conversations.IConversation import IConversation

class SemanticConversation(IConversation, ABC):
    """
    A concrete implementation of the Conversation class that includes semantic routing.
    Semantic routing involves analyzing the content of messages to understand their intent
    or category and then routing them to appropriate handlers based on that analysis.

    This class requires subclasses to implement the _analyze_message method for semantic analysis.
    """


    @abstractmethod
    def register_handler(self, category: str, handler: Callable[[IMessage], None]):
        """
        Registers a message handler for a specific semantic category.

        Args:
            category (str): The category of messages this handler should process.
            handler (Callable[[Message], None]): The function to call for messages of the specified category.
        """
        pass

    @abstractmethod
    def add_message(self, message: IMessage):
        """
        Adds a message to the conversation history and routes it to the appropriate handler based on its semantic category.

        Args:
            message (Message): The message to be added and processed.
        """
        pass

    @abstractmethod
    def _analyze_message(self, message: IMessage) -> Union[str, None]:
        """
        Analyzes the content of a message to determine its semantic category.

        This method must be implemented by subclasses to provide specific logic for semantic analysis.

        Args:
            message (Message): The message to analyze.

        Returns:
            Union[str, None]: The semantic category of the message, if determined; otherwise, None.

        Raises:
            NotImplementedError: If the method is not overridden in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the _analyze_message method to provide semantic analysis.")

    # Additional methods as needed for message retrieval, history management, etc., inherited from Conversation