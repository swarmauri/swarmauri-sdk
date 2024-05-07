from swarmauri.core.agents.IAgentVectorStore import IAgentVectorStore
from swarmauri.core.vector_stores.IVectorStore import IVectorStore


class VectorStoreAgentBase(IAgentVectorStore):
    def __init__(self, vector_store: IVectorStore):
        self._vector_store = vector_store  # vector store initialization

    @property
    def vector_store(self) -> IVectorStore:
        """
        Gets the vector store associated with this agent.
        
        Returns:
            IVectorStore: The new vector store to be associated with the agent.
        """
        return self._vector_store

    @vector_store.setter
    def vector_store(self, value: IVectorStore) -> None:
        """
        Sets the vector store for this agent.

        Args:
            value (IVectorStore): The new vector store to be associated with the agent.
        """
        self._vector_store = value
    
