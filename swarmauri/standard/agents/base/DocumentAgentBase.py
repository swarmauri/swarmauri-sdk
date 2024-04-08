from typing import Any, Optional
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.models.IModel import IModel
from swarmauri.core.conversations.IConversation import IConversation
from swarmauri.core.agents.IAgentDocument import IAgentDocumentStore
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore
from swarmauri.standard.agents.base.ConversationAgentBase import ConversationAgentBase
from swarmauri.standard.agents.base.NamedAgentBase import NamedAgentBase


class DocumentAgentBase(ConversationAgentBase, NamedAgentBase, IAgentDocumentStore):
    """
    Base class for agents that handle and store documents within their processing scope.
    Extends ConversationAgentBase and NamedAgentBase to utilize conversational context,
    naming capabilities, and implements IAgentDocumentStore for document storage.
    """

    def __init__(self, name: str, model: IModel, conversation: IConversation, document_store: IDocumentStore):
        NamedAgentBase.__init__(self, name=name)  # Initialize name through NamedAgentBase
        ConversationAgentBase.__init__(self, model, conversation)  # Initialize conversation and model
        self._document_store = document_store  # Document store initialization

    @property
    def document_store(self) -> Optional[IDocument]:
        """
        Gets the document store associated with this agent.
        
        Returns:
            Optional[IDocument]: The document store of the agent, if any.
        """
        return self._document_store

    @document_store.setter
    def document_store(self, value: IDocument) -> None:
        """
        Sets the document store for this agent.

        Args:
            value (IDocument): The new document store to be associated with the agent.
        """
        self._document_store = value
    
    def exec(self, input_data: Optional[Any]) -> Any:
        """
        Placeholder method to demonstrate expected behavior of derived classes.
        Subclasses should implement their specific logic for processing input data and optionally interacting with the document store.

        Args:
            input_data (Optional[Any]): Input data to process, can be of any format that the agent is designed to handle.

        Returns:
            Any: The result of processing the input data.
        """
        raise NotImplementedError("Subclasses must implement the exec method.")