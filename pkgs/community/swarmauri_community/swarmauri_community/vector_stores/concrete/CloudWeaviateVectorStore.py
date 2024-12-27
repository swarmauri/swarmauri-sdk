from typing import List, Union, Literal, Optional
from pydantic import BaseModel, PrivateAttr
import uuid as ud
import weaviate
from weaviate.classes.init import Auth
from weaviate.util import generate_uuid5
from weaviate.classes.query import MetadataQuery

from swarmauri.documents.concrete.Document import Document
from swarmauri_community.embeddings.concrete.Doc2VecEmbedding import Doc2VecEmbedding
from swarmauri.vectors.concrete.Vector import Vector

from swarmauri.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.vector_stores.base.VectorStoreRetrieveMixin import VectorStoreRetrieveMixin
from swarmauri.vector_stores.base.VectorStoreSaveLoadMixin import VectorStoreSaveLoadMixin
from swarmauri.vector_stores.base.VectorStoreCloudMixin import VectorStoreCloudMixin


class CloudWeaviateVectorStore(VectorStoreSaveLoadMixin, VectorStoreRetrieveMixin, VectorStoreBase, VectorStoreCloudMixin):
    type: Literal["CloudWeaviateVectorStore"] = "CloudWeaviateVectorStore"
    

    # Private attributes
    _client: Optional[weaviate.Client] = PrivateAttr(default=None)
    _embedder: Doc2VecEmbedding = PrivateAttr(default=None)
    _namespace_uuid: ud.UUID = PrivateAttr(default_factory=ud.uuid4)

    def __init__(self, **data):
        super().__init__(**data)

        # Initialize the vectorizer and Weaviate client
        self._embedder = Doc2VecEmbedding(vector_size=self.vector_size)
        # self._initialize_client()

    def connect(self, **kwargs):
        """
        Initialize the Weaviate client.
        """
        if self._client is None:
            self._client = weaviate.connect_to_weaviate_cloud(
                cluster_url=self.url,
                auth_credentials=Auth.api_key(self.api_key),
                headers=kwargs.get("headers", {})
            )
    
    def disconnect(self) -> None:
        """
        Disconnects from the Qdrant cloud vector store.
        """
        if self.client is not None:
            self.client = None

    def add_document(self, document: Document) -> None:
        """
        Add a single document to the vector store.

        :param document: Document to add
        """
        try:
            collection = self._client.collections.get(self.collection_name)

            # Generate or use existing embedding
            embedding = document.embedding or self._embedder.fit_transform([document.content])[0]

            data_object = {
                "content": document.content,
                "metadata": document.metadata,
            }

            # Generate UUID for document
            uuid = (
                str(ud.uuid5(self._namespace_uuid, document.id))
                if document.id
                else generate_uuid5(data_object)
            )

            collection.data.insert(
                properties=data_object,
                vector=embedding.value,
                uuid=uuid,
            )

            print(f"Document '{document.id}' added to Weaviate.")
        except Exception as e:
            print(f"Error adding document '{document.id}': {e}")
            raise

    def add_documents(self, documents: List[Document]) -> None:
        """
        Add multiple documents to the vector store.

        :param documents: List of documents to add
        """
        try:
            for document in documents:
                self.add_document(document)

            print(f"{len(documents)} documents added to Weaviate.")
        except Exception as e:
            print(f"Error adding documents: {e}")
            raise

    def get_document(self, id: str) -> Union[Document, None]:
        """
        Retrieve a document by its ID.

        :param id: Document ID
        :return: Document object or None if not found
        """
        try:
            collection = self._client.collections.get(self.collection_name)

            result = collection.query.fetch_object_by_id(ud.uuid5(self._namespace_uuid, id))

            if result:
                return Document(
                    id=id,
                    content=result.properties["content"],
                    metadata=result.properties["metadata"],
                )
            return None
        except Exception as e:
            print(f"Error retrieving document '{id}': {e}")
            return None

    def get_all_documents(self) -> List[Document]:
        """
        Retrieve all documents from the vector store.

        :return: List of Document objects
        """
        try:
            collection = self._client.collections.get(self.collection_name)
            # return collection
            documents = [
                Document(
                    content=item.properties["content"],
                    metadata=item.properties["metadata"],
                    embedding=Vector(value=list(item.vector.values())[0]),
                )
                for item in collection.iterator(include_vector=True)
            ]
            return documents
        except Exception as e:
            print(f"Error retrieving all documents: {e}")
            return []

    def delete_document(self, id: str) -> None:
        """
        Delete a document by its ID.

        :param id: Document ID
        """
        try:
            collection = self._client.collections.get(self.collection_name)
            collection.data.delete_by_id(ud.uuid5(self._namespace_uuid, id))
            print(f"Document '{id}' has been deleted from Weaviate.")
        except Exception as e:
            print(f"Error deleting document '{id}': {e}")
            raise

    def update_document(self, id: str, document: Document) -> None:
        """
        Update an existing document.

        :param id: Document ID
        :param updated_document: Document object with updated data
        """
        self.delete_document(id)
        self.add_document(document)

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        """
        Retrieve the top_k most relevant documents based on the given query.

        :param query: Query string
        :param top_k: Number of top similar documents to retrieve
        :return: List of Document objects
        """
        try:
            collection = self._client.collections.get(self.collection_name)
            query_vector = self._embedder.infer_vector(query)
            response = collection.query.near_vector(
                near_vector=query_vector.value,
                limit=top_k,
                return_metadata=MetadataQuery(distance=True),
            )

            documents = [
                Document(
                    # id=res.id,
                    content=res.properties["content"],
                    metadata=res.properties["metadata"],
                )
                for res in response.objects
            ]
            return documents
        except Exception as e:
            print(f"Error retrieving documents for query '{query}': {e}")
            return []

    def close(self):
        """
        Close the connection to the Weaviate server.
        """
        if self._client:
            self._client.close()

    def model_dump_json(self, *args, **kwargs) -> str:
        # Call the disconnect method before serialization
        self.disconnect()

        # Now proceed with the usual JSON serialization
        return super().model_dump_json(*args, **kwargs)

    
    def __del__(self):
        self.close()