from typing import List, Union, Literal
from weaviate.classes.query import MetadataQuery
import uuid as ud
import weaviate
from weaviate.classes.init import Auth
from weaviate.util import generate_uuid5
from swarmauri.vectors.concrete.Vector import Vector

from swarmauri.documents.concrete.Document import (
    Document,
)  # Replace with your actual import
from swarmauri.embeddings.concrete.Doc2VecEmbedding import (
    Doc2VecEmbedding,
)  # Replace with your actual import

from swarmauri.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.vector_stores.base.VectorStoreRetrieveMixin import (
    VectorStoreRetrieveMixin,
)
from swarmauri.vector_stores.base.VectorStoreSaveLoadMixin import (
    VectorStoreSaveLoadMixin,
)
from swarmauri.vector_stores.base.VectorStoreCloudMixin import (
    VectorStoreCloudMixin,
)

class CloudWeaviateVectorStore(
    VectorStoreSaveLoadMixin,
    VectorStoreRetrieveMixin,
    VectorStoreCloudMixin,
    VectorStoreBase,
):
    """
    CloudWeaviateVectorStore is a concrete implementation that integrates functionality
    for saving, loading, storing, and retrieving vector documents, leveraging Weaviate as the backend.
    """

    type: Literal["CloudWeaviateVectorStore"] = "CloudWeaviateVectorStore"

    def __init__(
        self, url: str, api_key: str, collection_name: str, vector_size: int, **kwargs
    ):
        self.url = url
        self.api_key = api_key
        self.collection_name = collection_name
        self.vector_size = vector_size

        self._embedder = Doc2VecEmbedding(vector_size=vector_size)
        self.vectorizer = self._embedder

        self.namespace_uuid = ud.uuid4()

        # Initialize Weaviate client with v4 authentication
        self.client = weaviate.connect_to_weaviate_cloud(
            cluster_url=self.url,
            auth_credentials=Auth.api_key(self.api_key),
            headers=kwargs.get("headers", {}),
        )

    def add_document(self, document: Document) -> None:
        """
        Add a single document to the vector store.
        """
        try:
            jeopardy = self.client.collections.get(self.collection_name)

            if not document.embedding:
                embedding = self.vectorizer.fit_transform([document.content])[0]
            else:
                embedding = document.embedding

            data_object = {
                "content": document.content,
                "metadata": document.metadata,
            }

            uuid = jeopardy.data.insert(
                properties=data_object,
                vector=embedding.value,
                uuid=(
                    str(ud.uuid5(self.namespace_uuid, document.id))
                    if document.id
                    else generate_uuid5(data_object)
                ),
            )

            print(f"Document '{document.id}' added to Weaviate.")
        except Exception as e:
            print(f"Error adding document '{document.id}': {e}")
            raise

    def add_documents(self, documents: List[Document]) -> None:
        """
        Add multiple documents to the vector store in a batch.
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
        Retrieve a single document by its identifier.
        """
        try:
            jeopardy = self.client.collections.get(self.collection_name)

            result = jeopardy.query.fetch_object_by_id(
                ud.uuid5(self.namespace_uuid, id)
            )

            if result:

                return Document(
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
        """
        try:
            collection = self.client.collections.get(self.collection_name)

            documents = [
                Document(
                    content=item.properties["content"],
                    metadata=item.properties["metadata"],
                    embedding=Vector(value=list(item.vector.values())[0]),
                )
                for item in collection.iterator(include_vector=True)
            ]
            print(documents[0])
            return documents
        except Exception as e:
            print(f"Error retrieving all documents: {e}")
            return []

    def delete_document(self, id: str) -> None:
        """
        Delete a document from the vector store by its identifier.
        """
        try:
            collection = self.client.collections.get(self.collection_name)
            collection.data.delete_by_id(ud.uuid5(self.namespace_uuid, id))
            print(f"Document '{id}' has been deleted from Weaviate.")
        except Exception as e:
            print(f"Error deleting document '{id}': {e}")
            raise

    def update_document(self, document: Document) -> None:
        self.delete_document(id)
        self.add_document(document)

    def document_count(self) -> int:
        """
        Returns the number of documents in the store.
        """
        try:
            result = (
                self.client.query.aggregate(self.collection_name).with_meta_count().do()
            )
            count = result["data"]["Aggregate"][self.collection_name][0]["meta"][
                "count"
            ]
            return count
        except Exception as e:
            print(f"Error counting documents: {e}")
            return 0

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        """
        Retrieve the top_k most relevant documents based on the given query.
        """
        try:
            jeopardy = self.client.collections.get(self.collection_name)
            query_vector = self.vectorizer.infer_vector(query)
            response = jeopardy.query.near_vector(
                near_vector=query_vector.value,  # your query vector goes here
                limit=top_k,
                return_metadata=MetadataQuery(distance=True),
            )

            documents = [
                Document(
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
        try:
            self.client.close()
        except Exception as e:
            print(f"Error closing connection: {e}")
            raise
