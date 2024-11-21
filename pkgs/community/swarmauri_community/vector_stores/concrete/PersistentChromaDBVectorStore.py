import logging
import chromadb
from chromadb.config import Settings

from typing import List, Union, Literal

from swarmauri.documents.concrete.Document import Document
from swarmauri_community.embeddings.concrete.Doc2VecEmbedding import Doc2VecEmbedding
from swarmauri.distances.concrete.CosineDistance import CosineDistance

from swarmauri.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.vector_stores.base.VectorStoreRetrieveMixin import (
    VectorStoreRetrieveMixin,
)
from swarmauri.vector_stores.base.VectorStoreSaveLoadMixin import (
    VectorStoreSaveLoadMixin,
)
from swarmauri.vector_stores.base.VectorStorePersistentMixin import (
    VectorStorePersistentMixin,
)


class PersistentChromaDBVectorStore(
    VectorStoreSaveLoadMixin,
    VectorStoreRetrieveMixin,
    VectorStorePersistentMixin,
    VectorStoreBase,
):
    type: Literal["PersistentChromaDBVectorStore"] = "PersistentChromaDBVectorStore"

    def __init__(self, **kwargs):
        """
        Initialize the PersistentChromaDBVectorStore.

        Args:
            Args:
            **kwargs: keyword arguments.
        """
        super().__init__(**kwargs)

        self._embedder = Doc2VecEmbedding(vector_size=self.vector_size)
        self._distance = CosineDistance()

    def connect(self) -> None:
        """
        Establish a connection to ChromaDB and get or create the collection.
        """
        # settings = Settings(
        #     chroma_api_impl="chromadb.api.fastapi.FastAPI",  # Use FastAPI if LocalAPI is not supported
        #     chroma_server_host="localhost",  # Server host
        #     chroma_server_http_port=8000,  # Server port
        # )
        #
        # self.client = chromadb.Client(
        #     settings=settings,
        # )
        self.client = chromadb.Client()

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )
        logging.info(
            f"Connected to ChromaDB at {self.path}, collection: {self.collection_name}"
        )

    def disconnect(self) -> None:
        """
        Close the connection to ChromaDB.
        """
        if self.client:
            # Perform any necessary cleanup here
            self.client = None
            self.collection = None

    def add_document(self, document: Document) -> None:
        embedding = None
        if not document.embedding:
            self._embedder.fit([document.content])  # Fit only once
            embedding = (
                self._embedder.transform([document.content])[0].to_numpy().tolist()
            )
        else:
            embedding = document.embedding

        self.collection.add(
            ids=[document.id],
            documents=[document.content],
            embeddings=[embedding],
            metadatas=[document.metadata],
        )

    def add_documents(self, documents: List[Document]) -> None:
        ids = [doc.id for doc in documents]
        texts = [doc.content for doc in documents]

        for doc in documents:
            self._embedder.fit([doc.content])

        embeddings = [
            self._embedder.infer_vector(doc.content).value for doc in documents
        ]
        metadatas = [doc.metadata for doc in documents]
        if metadatas[0]:
            self.collection.add(
                ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas
            )
        else:
            self.collection.add(ids=ids, documents=texts, embeddings=embeddings)

    def get_document(self, doc_id: str) -> Union[Document, None]:
        results = self.collection.get(ids=[doc_id])
        if not results["metadatas"][0]:
            results["metadatas"][0] = {}
        if results["ids"]:
            document = Document(
                id=results["ids"][0],
                content=results["documents"][0],
                metadata=results["metadatas"][0],
            )
            return document
        return None

    def get_all_documents(self) -> List[Document]:
        results = self.collection.get()
        documents = [
            Document(
                id=results["ids"][idx],
                content=results["documents"][idx],
                metadata=results["metadatas"][idx],
            )
            for idx in range(len(results["ids"]))
        ]
        return documents

    def delete_document(self, doc_id: str) -> None:
        self.collection.delete(ids=[doc_id])

    def update_document(self, doc_id: str, updated_document: Document) -> None:
        document_vector = None
        # Precompute the embedding outside the update process
        if not updated_document.embedding:
            # Transform without refitting to avoid vocabulary issues
            document_vector = self._embedder.transform([updated_document.content])[0]
        else:
            document_vector = updated_document.embedding

        document_vector = document_vector.to_numpy().tolist()

        updated_document.embedding = document_vector

        self.delete_document(doc_id)
        self.add_document(updated_document)

    def clear_documents(self) -> None:
        documents = self.get_all_documents()
        doc_ids = [doc.id for doc in documents]
        self.collection.delete(ids=doc_ids)

    def document_count(self) -> int:
        return len(self.get_all_documents())

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        query_embedding = self._embedder.infer_vector(query).value
        # print(query_embedding)

        results = self.collection.query(
            query_embeddings=query_embedding, n_results=top_k
        )

        return [
            Document(
                id=results["ids"][0][idx],
                content=results["documents"][0][idx],
                metadata=(
                    results["metadatas"][0][idx] if results["metadatas"][0][idx] else {}
                ),
            )
            for idx in range(len(results["ids"][0]))
        ]

    # Override the model_dump_json method
    def model_dump_json(self, *args, **kwargs) -> str:
        # Call the disconnect method before serialization
        self.disconnect()

        # Now proceed with the usual JSON serialization
        return super().model_dump_json(*args, **kwargs)
