from typing import List
from redisearch import Client, Query
from ....core.documents.IDocument import IDocument
from ....standard.document_stores.concrete.ConcreteDocument import ConcreteDocument
from ....standard.retrievers.base.DocumentRetrieverBase import DocumentRetrieverBase

class RedisDocumentRetriever(DocumentRetrieverBase):
    """
    A document retriever that fetches documents from a Redis store.
    """
    
    def __init__(self, redis_idx_name, redis_host, redis_port):
        """
        Initializes a new instance of RedisDocumentRetriever.

        Args:
            redis_client (Redis): An instance of the Redis client.
        """
        self._redis_client = None
        self._redis_idx_name = redis_idx_name
        self._redis_host = redis_host
        self._redis_port = redis_port

    @property
    def redis_client(self):
        """Lazily initialize and return the Redis client using a factory method."""
        if self._redis_client is None:
            self._redis_client = Client(self.redis_idx_name, host=self.redis_host, port=self.redis_port)
        return self._redis_client
    
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve the most relevant documents based on the given query.
        
        Args:
            query (str): The query string used for document retrieval.
            top_k (int, optional): The number of top relevant documents to retrieve. Defaults to 5.
        
        Returns:
            List[IDocument]: A list of the top_k most relevant documents.
        """
        query_result = self.redis_client.search(Query(query).paging(0, top_k))
        
        documents = [
            ConcreteDocument(
                doc_id=doc.id,
                content=doc.text,  # Note: Adjust 'text' based on actual Redis document schema
                metadata=doc.__dict__  # Including full document fields and values in metadata
            )
            for doc in query_result.docs
        ]

        return documents
