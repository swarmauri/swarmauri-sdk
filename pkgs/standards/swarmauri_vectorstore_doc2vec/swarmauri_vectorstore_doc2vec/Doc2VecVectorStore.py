from typing import List, Union, Literal

from swarmauri_standard.documents.Document import Document
from swarmauri_base.vector_stores.VectorStoreBase import VectorStoreBase
from swarmauri_base.vector_stores.VectorStoreRetrieveMixin import (
    VectorStoreRetrieveMixin,
)
from swarmauri_base.vector_stores.VectorStoreSaveLoadMixin import (
    VectorStoreSaveLoadMixin,
)
from swarmauri_embedding_doc2vec.Doc2VecEmbedding import (
    Doc2VecEmbedding,
)
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_standard.vector_stores.CosineSimilarityComparator import (
    CosineSimilarityComparator,
)


@ComponentBase.register_type(VectorStoreBase, "Doc2VecVectorStore")
class Doc2VecVectorStore(
    VectorStoreSaveLoadMixin, VectorStoreRetrieveMixin, VectorStoreBase
):
    type: Literal["Doc2VecVectorStore"] = "Doc2VecVectorStore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._embedder = Doc2VecEmbedding()
        self._comparator = CosineSimilarityComparator()

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

        # Rank documents by descending cosine similarity.
        top_k_indices = self._comparator.top_k_indices(
            query_vector, document_vectors, top_k
        )

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
