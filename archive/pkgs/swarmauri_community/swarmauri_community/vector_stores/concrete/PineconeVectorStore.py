import numpy as np
from typing import List, Union, Literal, Dict, Any, Optional

from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec

from swarmauri.documents.concrete.Document import Document
from swarmauri_community.embeddings.concrete.Doc2VecEmbedding import Doc2VecEmbedding
from swarmauri.distances.concrete.CosineDistance import CosineDistance

from swarmauri.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.vector_stores.base.VectorStoreRetrieveMixin import (
    VectorStoreRetrieveMixin,
)
from swarmauri.vector_stores.base.VectorStoreCloudMixin import (
    VectorStoreCloudMixin,
)
from swarmauri.vector_stores.base.VectorStoreSaveLoadMixin import (
    VectorStoreSaveLoadMixin,
)


class PineconeVectorStore(
    VectorStoreRetrieveMixin,
    VectorStoreCloudMixin,
    VectorStoreSaveLoadMixin,
    VectorStoreBase,
):
    """
    A vector store implementation using Pinecone as the backend.

    This class provides methods to interact with a Pinecone index, including
    adding, retrieving, updating, and deleting documents, as well as performing
    similarity searches.
    """

    type: Literal["PineconeVectorStore"] = "PineconeVectorStore"

    def __init__(self, **kwargs):
        """
        Initialize the PineconeVectorStore.
        Args:
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self._embedder = Doc2VecEmbedding(vector_size=self.vector_size)
        self._distance = CosineDistance()

    def delete(self):
        """
        Delete the Pinecone index if it exists.

        """
        try:
            pc = Pinecone(api_key=self.api_key)
            pc.delete_index(self.collection_name)
            self.client = None
        except Exception as e:
            raise RuntimeError(
                f"Failed to delete index {self.collection_name}: {str(e)}"
            )

    def connect(self, metric: Optional[str] = "cosine", cloud: Optional[str] = "aws", region: Optional[str] = "us-east-1"):
        """
        Connect to the Pinecone index, creating it if it doesn't exist.

        Args:
            metric (Optional[str]): The distance metric to use. Defaults to "cosine".
            cloud (Optional[str]): The cloud provider to use. Defaults to "aws".
            region (Optional[str]): The region to use. Defaults to "us-east-1".

        """
        try:
            pc = Pinecone(api_key=self.api_key)
            if not pc.has_index(self.collection_name):
                pc.create_index(
                    name=self.collection_name,
                    dimension=self.vector_size,
                    metric=metric,
                    spec=ServerlessSpec(
                        cloud=cloud,
                        region=region,
                    ),
                )
            self.client = pc.Index(self.collection_name)
        except Exception as e:
            raise RuntimeError(
                f"Failed to connect to Pinecone index {self.collection_name}: {str(e)}"
            )

    def disconnect(self):
        """
        Disconnect from the Pinecone index.

        """
        try:
            self.client = None
        except Exception as e:
            raise RuntimeError(f"Error during disconnecting: {str(e)}")

    def _prepare_vector(self, document: Document) -> Dict[str, Any]:
        """
        Prepare a vector for insertion into the Pinecone index.

        Args:
            document (Document): The document to prepare.

        Returns:
            Dict[str, Any]: A dictionary containing the prepared vector data.
        """
        embedding = None
        if not document.embedding:
            self._embedder.fit([document.content])
            embedding = (
                self._embedder.transform([document.content])[0].to_numpy().tolist()
            )
        else:
            embedding = document.embedding

        document.metadata["content"] = document.content
        return {"id": document.id, "values": embedding, "metadata": document.metadata}

    def add_document(self, document: Document, namespace: Optional[str] = "") -> None:
        """
        Add a single document to the Pinecone index.

        Args:
            document (Document): The document to add.
            namespace (Optional[str]): The namespace to add the document to. Defaults to "".
        """
        try:
            vector = self._prepare_vector(document)
            self.client.upsert(vectors=[vector], namespace=namespace)
        except Exception as e:
            raise RuntimeError(f"Failed to add document {document.id}: {str(e)}")

    def add_documents(
        self,
        documents: List[Document],
        namespace: Optional[str] = "",
        batch_size: int = 200,
    ) -> None:
        """
        Add multiple documents to the Pinecone index in batches.

        Args:
            documents (List[Document]): The list of documents to add.
            namespace (Optional[str]): The namespace to add the documents to. Defaults to "".
            batch_size (int): The number of documents to add in each batch. Defaults to 200.

        """
        if batch_size <= 0 or batch_size > 1000:
            raise ValueError("Batch size must be between 1 and 1000.")

        vectors = [self._prepare_vector(doc) for doc in documents]
        for i in range(0, len(vectors), batch_size):
            batch_vectors = vectors[i : i + batch_size]
            try:
                self.client.upsert(vectors=batch_vectors, namespace=namespace)
            except Exception as e:
                raise RuntimeError(
                    f"Error during batch upsert. Consider lowering batch size: {str(e)}"
                )

    def get_document(
        self, id: str, namespace: Optional[str] = ""
    ) -> Union[Document, None]:
        """
        Retrieve a single document from the Pinecone index by its ID.

        Args:
            id (str): The ID of the document to retrieve.
            namespace (Optional[str]): The namespace to search in. Defaults to "".

        Returns:
            Union[Document, None]: The retrieved document, or None if not found.

        """
        try:
            result = self.client.fetch(ids=[id], namespace=namespace)
            if id in result["vectors"]:
                vector = result["vectors"][id]
                return Document(
                    id=id,
                    content=vector["metadata"].get("content", ""),
                    metadata=vector["metadata"] or {},
                )
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to get document {id}: {str(e)}")

    def _get_ids_from_query(self, input_vector):
        """
        Get document IDs from a query vector.

        Args:
            input_vector: The input vector to query.

        """
        results = self.client.query(
            vector=input_vector, top_k=10000, include_values=False
        )
        return {result["id"] for result in results["matches"]}

    def _get_all_ids_from_client(self, namespace: Optional[str] = ""):
        """
        Get all document IDs from the Pinecone index.

        Args:
            namespace (Optional[str]): The namespace to search in. Defaults to "".

        Returns:
            set: A set of all document IDs in the index.
        """
        num_vectors = self.client.describe_index_stats()["namespaces"][namespace][
            "vector_count"
        ]
        all_ids = set()
        while len(all_ids) < num_vectors:
            input_vector = np.random.rand(self.vector_size).tolist()
            ids = self._get_ids_from_query(input_vector)
            all_ids.update(ids)
        return all_ids

    def get_all_documents(self, namespace: Optional[str] = "") -> List[Document]:
        """
        Retrieve all documents from the Pinecone index.

        Args:
            namespace (Optional[str]): The namespace to search in. Defaults to "".

        Returns:
            List[Document]: A list of all documents in the index.

        """
        try:
            documents = []
            id_list = list(self._get_all_ids_from_client(namespace))
            batch_size = min(len(id_list), 1000)
            for i in range(0, len(id_list), batch_size):
                batch_ids = id_list[i : i + batch_size]
                result = self.client.fetch(ids=batch_ids, namespace=namespace)
                for id, vector in result["vectors"].items():
                    documents.append(
                        Document(
                            id=id,
                            content=vector["metadata"].get("content", ""),
                            metadata=vector["metadata"] or {},
                        )
                    )
            return documents
        except Exception as e:
            raise RuntimeError(f"Failed to get all documents: {str(e)}")

    def delete_document(self, id: str, namespace: Optional[str] = "") -> None:
        """
        Delete a single document from the Pinecone index.

        Args:
            id (str): The ID of the document to delete.
            namespace (Optional[str]): The namespace to delete from. Defaults to "".

        """
        try:
            self.client.delete(ids=[id], namespace=namespace)
        except Exception as e:
            raise RuntimeError(f"Failed to delete document {id}: {str(e)}")

    def clear_documents(self, namespace: Optional[str] = "") -> None:
        """
        Delete all documents from the Pinecone index in a given namespace.

        Args:
            namespace (Optional[str]): The namespace to clear. Defaults to "".

        """
        try:
            self.client.delete(delete_all=True, namespace=namespace)
        except Exception as e:
            raise RuntimeError(
                f"Failed to clear documents in namespace {namespace}: {str(e)}"
            )

    def update_document(
        self, id: str, document: Document, namespace: Optional[str] = ""
    ) -> None:
        """
        Update a document in the Pinecone index.

        Args:
            id (str): The ID of the document to update.
            document (Document): The updated document.
            namespace (Optional[str]): The namespace of the document. Defaults to "".

        """
        try:
            embedding = (
                self._embedder.transform([document.content])[0].to_numpy().tolist()
            )
            document.metadata["content"] = document.content
            self.client.update(
                id=id,
                values=embedding,
                set_metadata=document.metadata,
                namespace=namespace,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to update document {id}: {str(e)}")

    def document_count(self, namespace: Optional[str] = "") -> int:
        """
        Get the number of documents in the Pinecone index.

        Args:
            namespace (Optional[str]): The namespace to count documents in. Defaults to "".

        Returns:
            int: The number of documents in the index.

        """
        try:
            return self.client.describe_index_stats()["namespaces"][namespace][
                "vector_count"
            ]
        except Exception as e:
            raise RuntimeError(
                f"Failed to get document count for namespace {namespace}: {str(e)}"
            )

    def retrieve(
        self, query: str, top_k: int = 5, namespace: Optional[str] = ""
    ) -> List[Document]:
        """
        Retrieve documents from the Pinecone index based on a query string.

        Args:
            query (str): The query string to search for.
            top_k (int): The number of results to return. Defaults to 5.
            namespace (Optional[str]): The namespace to search in. Defaults to "".

        Returns:
            List[Document]: A list of retrieved documents.

        """
        try:
            query_embedding = self._embedder.infer_vector(query).value
            results = self.client.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=namespace,
                include_metadata=True,
            )
            return [
                Document(
                    id=match["id"],
                    content=match["metadata"].get("content", ""),
                    metadata=match["metadata"] or {},
                )
                for match in results["matches"]
            ]
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve documents: {str(e)}")

    # Override the model_dump_json method
    def model_dump_json(self, *args, **kwargs) -> str:
        # Call the disconnect method before serialization
        self.disconnect()

        # Now proceed with the usual JSON serialization
        return super().model_dump_json(*args, **kwargs)
