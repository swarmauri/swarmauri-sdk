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


class Doc2VecVectorStore(
    VectorStoreSaveLoadMixin, VectorStoreRetrieveMixin, VectorStoreBase
):
    type: Literal["Doc2VecVectorStore"] = "Doc2VecVectorStore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._embedder = Doc2VecEmbedding()
        self._distance = CosineDistance()

    def add_document(self, document: Document) -> None:
        self._embedder.fit([document.content])
        self.documents.append(document)

    def add_documents(self, documents: List[Document]) -> None:
        self.documents.extend(documents)
        self._embedder.fit([doc.content for doc in documents])

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        query_vector = self._embedder.infer_vector(query)

        # If the query vector is all-zero, return an empty list
        if all(v == 0.0 for v in query_vector.value):
            print("Query contains only OOV words.")
            return []

        # Transform the stored documents into vectors
        document_vectors = self._embedder.transform(
            [doc.content for doc in self.documents]
        )

        # Calculate cosine distances between the query vector and document vectors
        distances = self._distance.distances(query_vector, document_vectors)

        # Get the indices of the top_k closest documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[
            :top_k
        ]

        return [self.documents[i] for i in top_k_indices]

    def get_document(self, id: str) -> Union[Document, None]:
        for document in self.documents:
            if document.id == id:
                return document
        return None

    def get_all_documents(self) -> List[Document]:
        return self.documents

    def delete_document(self, id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != id]
        self._embedder.fit([doc.content for doc in self.documents])

    def update_document(self, id: str, updated_document: Document) -> None:
        for i, document in enumerate(self.documents):
            if document.id == id:
                self.documents[i] = updated_document
                break
        self._embedder.fit([doc.content for doc in self.documents])
