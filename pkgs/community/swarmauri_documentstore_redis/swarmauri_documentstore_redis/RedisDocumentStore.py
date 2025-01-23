from typing import List, Literal, Optional

from pydantic import PrivateAttr
from swarmauri_core.ComponentBase import ComponentBase
from swarmauri_base.document_stores.DocumentStoreBase import DocumentStoreBase
from swarmauri_standard.documents.Document import Document
import redis
import json


@ComponentBase.register_type(DocumentStoreBase, "RedisDocumentStore")
class RedisDocumentStore(DocumentStoreBase):
    # Public fields
    type: Literal["RedisDocumentStore"] = "RedisDocumentStore"

    # Private attributes
    _host: str = PrivateAttr()
    _password: str = PrivateAttr()
    _port: int = PrivateAttr()
    _db: int = PrivateAttr()
    _redis_client: Optional[redis.Redis] = PrivateAttr(default=None)

    def __init__(
        self, host: str, password: str = "", port: int = 6379, db: int = 0, **data
    ):
        super().__init__(**data)
        self._host = host
        self._password = password
        self._port = port
        self._db = db

    @property
    def redis_client(self):
        """Lazily initialize and return the Redis client using a factory method."""
        if self._redis_client is None:
            print("here")
            self._redis_client = redis.Redis(
                host=self._host, password=self._password, port=self._port, db=self._db
            )
            print("there")
        return self._redis_client

    def add_document(self, document: Document) -> None:

        data = document.model_dump()
        doc_id = data.pop("id")  # Remove and get id
        self.redis_client.json().set(doc_id, "$", json.dumps(data))

    def add_documents(self, documents: List[Document]) -> None:
        with self.redis_client.pipeline() as pipe:
            for document in documents:
                data = document.model_dump()
                doc_id = data.pop("id")
                pipe.json().set(doc_id, "$", json.dumps(data))
            pipe.execute()

    def get_document(self, doc_id: str) -> Optional[Document]:
        result = self.redis_client.json().get(doc_id)
        if result:
            return json.loads(result)
        return None

    def get_all_documents(self) -> List[Document]:
        keys = self.redis_client.keys("*")
        documents = []
        for key in keys:
            document_data = self.redis_client.get(key)
            if document_data:
                documents.append(json.loads(document_data))
        return documents

    def update_document(self, doc_id: str, document: Document) -> None:
        data = document.model_dump()
        data.pop("id")  # Remove id from data
        self.redis_client.json().set(doc_id, "$", json.dumps(data))

    def delete_document(self, doc_id: str) -> None:
        self.redis_client.delete(doc_id)

    def __getstate__(self):
        """Return the object state for serialization, excluding the Redis client."""
        state = self.__dict__.copy()
        state["_redis_client"] = None  # Exclude Redis client from serialization
        return state

    def __setstate__(self, state):
        """Restore the object state after serialization, reinitializing the Redis client."""
        self.__dict__.update(state)
