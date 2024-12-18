from typing import List, Union, Literal, Dict, Any, Optional
import numpy as np
from annoy import AnnoyIndex
import os

from swarmauri.documents.concrete.Document import Document
from swarmauri_community.embeddings.concrete.Doc2VecEmbedding import Doc2VecEmbedding
from swarmauri.distances.concrete.CosineDistance import CosineDistance

from swarmauri.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.vector_stores.base.VectorStoreRetrieveMixin import (
    VectorStoreRetrieveMixin,
)
from swarmauri.vector_stores.base.VectorStoreCloudMixin import VectorStoreCloudMixin
from swarmauri.vector_stores.base.VectorStoreSaveLoadMixin import (
    VectorStoreSaveLoadMixin,
)


class AnnoyVectorStore(
    VectorStoreRetrieveMixin,
    VectorStoreCloudMixin,
    VectorStoreSaveLoadMixin,
    VectorStoreBase,
):
    """
    A vector store implementation using Annoy as the backend.

    This class provides methods to interact with an Annoy index, including
    adding, retrieving, and searching for documents. Note that Annoy indices
    are immutable after building, so updates and deletes require rebuilding.
    """

    type: Literal["AnnoyVectorStore"] = "AnnoyVectorStore"
    api_key: str = (
        "not_required"  # Annoy doesn't need an API key, but base class requires it
    )

    def __init__(self, **kwargs):
        """
        Initialize the AnnoyVectorStore.
        Args:
            **kwargs: Additional keyword arguments.
        """
        # Set default api_key if not provided
        if "api_key" not in kwargs:
            kwargs["api_key"] = "not_required"

        super().__init__(**kwargs)
        self._embedder = Doc2VecEmbedding(vector_size=self.vector_size)
        self._distance = CosineDistance()
        self.client = None
        self._documents = (
            {}
        )  # Store documents in memory since Annoy only stores vectors
        self._current_index = 0  # Track the next available index
        self._id_to_index = {}  # Map document IDs to Annoy indices
        self._index_to_id = {}  # Map Annoy indices to document IDs

    def delete(self):
        """
        Delete the Annoy index if it exists.
        """
        try:
            if os.path.exists(f"{self.collection_name}.ann"):
                os.remove(f"{self.collection_name}.ann")
            self.client = None
            self._documents = {}
            self._current_index = 0
            self._id_to_index = {}
            self._index_to_id = {}
        except Exception as e:
            raise RuntimeError(
                f"Failed to delete index {self.collection_name}: {str(e)}"
            )

    def connect(self, metric: Optional[str] = "angular", n_trees: int = 10):
        """
        Connect to the Annoy index, creating it if it doesn't exist.

        Args:
            metric (Optional[str]): The distance metric to use. Defaults to "angular".
            n_trees (int): Number of trees for the Annoy index. More trees = better accuracy but larger index.
        """
        try:
            self.client = AnnoyIndex(self.vector_size, metric)
            if os.path.exists(f"{self.collection_name}.ann"):
                self.client.load(f"{self.collection_name}.ann")
        except Exception as e:
            raise RuntimeError(
                f"Failed to connect to Annoy index {self.collection_name}: {str(e)}"
            )

    def disconnect(self):
        """
        Disconnect from the Annoy index.
        """
        try:
            self.client = None
        except Exception as e:
            raise RuntimeError(f"Error during disconnecting: {str(e)}")

    def _prepare_vector(self, document: Document) -> np.ndarray:
        """
        Prepare a vector for insertion into the Annoy index.

        Args:
            document (Document): The document to prepare.

        Returns:
            np.ndarray: The prepared vector.
        """
        if not document.embedding:
            self._embedder.fit([document.content])
            embedding = self._embedder.transform([document.content])[0].to_numpy()
        else:
            embedding = np.array(document.embedding)
        return embedding

    def add_document(self, document: Document, namespace: Optional[str] = "") -> None:
        """
        Add a single document to the Annoy index.
        Note: In Annoy, the index needs to be rebuilt after adding documents.

        Args:
            document (Document): The document to add.
            namespace (Optional[str]): Not used in Annoy but kept for compatibility.
        """
        try:
            vector = self._prepare_vector(document)
            index = self._current_index
            self.client.add_item(index, vector)
            self._documents[document.id] = document
            self._id_to_index[document.id] = index
            self._index_to_id[index] = document.id
            self._current_index += 1
        except Exception as e:
            raise RuntimeError(f"Failed to add document {document.id}: {str(e)}")

    def add_documents(
        self,
        documents: List[Document],
        namespace: Optional[str] = "",
        batch_size: int = 200,
    ) -> None:
        """
        Add multiple documents to the Annoy index.
        Note: The index will be built after adding all documents.

        Args:
            documents (List[Document]): The list of documents to add.
            namespace (Optional[str]): Not used in Annoy but kept for compatibility.
            batch_size (int): Not used in Annoy but kept for compatibility.
        """
        try:
            for document in documents:
                self.add_document(document, namespace)
            self.client.build(10)  # Build with default 10 trees
            self.client.save(f"{self.collection_name}.ann")
        except Exception as e:
            raise RuntimeError(f"Failed to add documents: {str(e)}")

    def get_document(
        self, id: str, namespace: Optional[str] = ""
    ) -> Union[Document, None]:
        """
        Retrieve a single document by its ID.

        Args:
            id (str): The ID of the document to retrieve.
            namespace (Optional[str]): Not used in Annoy but kept for compatibility.

        Returns:
            Union[Document, None]: The retrieved document, or None if not found.
        """
        return self._documents.get(id)

    def get_all_documents(self, namespace: Optional[str] = "") -> List[Document]:
        """
        Retrieve all documents.

        Args:
            namespace (Optional[str]): Not used in Annoy but kept for compatibility.

        Returns:
            List[Document]: A list of all documents.
        """
        return list(self._documents.values())

    def delete_document(self, id: str, namespace: Optional[str] = "") -> None:
        """
        Delete a single document.
        Note: This requires rebuilding the index.

        Args:
            id (str): The ID of the document to delete.
            namespace (Optional[str]): Not used in Annoy but kept for compatibility.
        """
        try:
            if id in self._documents:
                del self._documents[id]
                index = self._id_to_index[id]
                del self._id_to_index[id]
                del self._index_to_id[index]
                # Rebuild index with remaining documents
                self.client = AnnoyIndex(self.vector_size, "angular")
                for doc_id, doc in self._documents.items():
                    vector = self._prepare_vector(doc)
                    self.client.add_item(self._id_to_index[doc_id], vector)
                self.client.build(10)
                self.client.save(f"{self.collection_name}.ann")
        except Exception as e:
            raise RuntimeError(f"Failed to delete document {id}: {str(e)}")

    def clear_documents(self, namespace: Optional[str] = "") -> None:
        """
        Delete all documents.

        Args:
            namespace (Optional[str]): Not used in Annoy but kept for compatibility.
        """
        try:
            self.delete()
            self.connect()
        except Exception as e:
            raise RuntimeError(f"Failed to clear documents: {str(e)}")

    def update_document(
        self, id: str, document: Document, namespace: Optional[str] = ""
    ) -> None:
        """
        Update a document.
        Note: This requires rebuilding the index.

        Args:
            id (str): The ID of the document to update.
            document (Document): The updated document.
            namespace (Optional[str]): Not used in Annoy but kept for compatibility.
        """
        try:
            self.delete_document(id, namespace)
            self.add_document(document, namespace)
        except Exception as e:
            raise RuntimeError(f"Failed to update document {id}: {str(e)}")

    def document_count(self, namespace: Optional[str] = "") -> int:
        """
        Get the number of documents in the index.

        Args:
            namespace (Optional[str]): Not used in Annoy but kept for compatibility.

        Returns:
            int: The number of documents in the index.
        """
        return len(self._documents)

    def retrieve(
        self, query: str, top_k: int = 5, namespace: Optional[str] = ""
    ) -> List[Document]:
        """
        Retrieve documents based on a query string.

        Args:
            query (str): The query string to search for.
            top_k (int): The number of results to return. Defaults to 5.
            namespace (Optional[str]): Not used in Annoy but kept for compatibility.

        Returns:
            List[Document]: A list of retrieved documents.
        """
        try:
            query_embedding = self._embedder.infer_vector(query).value
            indices, distances = self.client.get_nns_by_vector(
                query_embedding, top_k, include_distances=True
            )
            results = []
            for idx in indices:
                doc_id = self._index_to_id.get(idx)
                if doc_id:
                    results.append(self._documents[doc_id])
            return results
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve documents: {str(e)}")

    def model_dump_json(self, *args, **kwargs) -> str:
        """
        Override the model_dump_json method to ensure proper serialization.
        """
        self.disconnect()
        return super().model_dump_json(*args, **kwargs)
