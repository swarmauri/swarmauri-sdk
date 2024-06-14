from typing import List, Union
from pydantic import PrivateAttr

from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.embedddings.concrete.Doc2VecEmbedding import Doc2VecEmbedding
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance

from swarmauri.standard.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.standard.vector_stores.base.VectorStoreRetrieveMixin import VectorStoreRetrieveMixin
from swarmauri.standard.vector_stores.base.VectorStoreSaveLoadMixin import VectorStoreSaveLoadMixin    


class Doc2VecVectorStore(VectorStoreSaveLoadMixin, VectorStoreRetrieveMixin, VectorStoreBase):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._embedding = Doc2VecEmbedding()
        self._distance = CosineDistance()

    def add_document(self, document: Document) -> None:
        self.documents.append(document)
        self._recalculate_embeddings()

    def add_documents(self, documents: List[Document]) -> None:
        self.documents.extend(documents)
        self._recalculate_embeddings()

    def get_document(self, id: str) -> Union[Document, None]:
        for document in self.documents:
            if document.id == id:
                return document
        return None

    def get_all_documents(self) -> List[Document]:
        return self.documents

    def delete_document(self, id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != id]
        self._recalculate_embeddings()

    def update_document(self, id: str, updated_document: Document) -> None:
        for i, document in enumerate(self.documents):
            if document.id == id:
                self.documents[i] = updated_document
                break
        self._recalculate_embeddings()

    def _recalculate_embeddings(self):
        # Recalculate document embeddings for the current set of documents
        documents_text = [_d.content for _d in self.documents if _d.content]
        embeddings = self._embedding.fit_transform(documents_text)

        embedded_documents = [Document(id=_d.id, 
            content=_d.content, 
            metadata=_d.metadata, 
            embedding=embeddings[_count]) for _count, _d in enumerate(self.documents)
            if _d.content]

        self.documents = embedded_documents

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        query_vector = self._vectorizer.infer_vector(query)
        document_vectors = [_d.embedding for _d in self.documents if _d.content]

        distances = self._distance.distances(query_vector, document_vectors)

        # Get the indices of the top_k least distant (most similar) documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:top_k]
        
        return [self.documents[i] for i in top_k_indices]