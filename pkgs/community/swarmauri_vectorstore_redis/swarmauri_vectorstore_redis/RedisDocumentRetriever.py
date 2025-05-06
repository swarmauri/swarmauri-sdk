from typing import List, Optional

from pydantic import Field, PrivateAttr
from redisearch import Client, Query
from swarmauri_base.document_stores.DocumentStoreRetrieveBase import (
    DocumentStoreRetrieveBase,
)
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_standard.documents.Document import Document


@ComponentBase.register_type(DocumentStoreRetrieveBase, "RedisDocumentRetriever")
class RedisDocumentRetriever(DocumentStoreRetrieveBase):
    """
    A document retriever that fetches documents from a Redis store.
    """

    type: str = "RedisDocumentRetriever"
    redis_idx_name: str = Field(..., description="Redis index name")
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")

    # Private attributes
    _redis_client: Optional[Client] = PrivateAttr(default=None)

    @property
    def redis_client(self) -> Client:
        """Lazily initialize and return the Redis client using a factory method."""
        if self._redis_client is None:
            self._redis_client = Client(
                self.redis_idx_name, host=self.redis_host, port=self.redis_port
            )
        return self._redis_client

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        """
        Retrieve the most relevant documents based on the given query.

        Args:
            query (str): The query string used for document retrieval.
            top_k (int, optional): The number of top relevant documents to retrieve. Defaults to 5.

        Returns:
            List[Document]: A list of the top_k most relevant documents.
        """
        query_result = self.redis_client.search(Query(query).paging(0, top_k))

        documents = [
            Document(
                id=doc.id,
                content=doc.content,  # Note: Adjust 'text' based on actual Redis document schema
                metadata=doc.__dict__,  # Including full document fields and values in metadata
            )
            for doc in query_result.docs
        ]

        return documents
