from typing import List, Union
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.vectorizers.concrete.TFIDFVectorizer import TFIDFVectorizer
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vector_stores.base.VectorDocumentStoreRetrieveBase import VectorDocumentStoreRetrieveBase
from swarmauri.standard.vector_stores.base.SaveLoadStoreBase import SaveLoadStoreBase

class TFIDFVectorStore(VectorDocumentStoreRetrieveBase, SaveLoadStoreBase):
    def __init__(self):
        self.vectorizer = TFIDFVectorizer()
        self.metric = CosineDistance()
        self.documents = []
        SaveLoadStoreBase.__init__(self, self.vectorizer, self.documents)
      

    def add_document(self, document: IDocument) -> None:
        self.documents.append(document)
        # Recalculate TF-IDF matrix for the current set of documents
        self.vectorizer.fit([doc.content for doc in self.documents])

    def add_documents(self, documents: List[IDocument]) -> None:
        self.documents.extend(documents)
        # Recalculate TF-IDF matrix for the current set of documents
        self.vectorizer.fit([doc.content for doc in self.documents])

    def get_document(self, doc_id: str) -> Union[IDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None

    def get_all_documents(self) -> List[IDocument]:
        return self.documents

    def delete_document(self, doc_id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != doc_id]
        # Recalculate TF-IDF matrix for the current set of documents
        self.vectorizer.fit([doc.content for doc in self.documents])

    def update_document(self, doc_id: str, updated_document: IDocument) -> None:
        for i, document in enumerate(self.documents):
            if document.id == doc_id:
                self.documents[i] = updated_document
                break

        # Recalculate TF-IDF matrix for the current set of documents
        self.vectorizer.fit([doc.content for doc in self.documents])

    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        transform_matrix = self.vectorizer.fit_transform(query, self.documents)

        # The inferred vector is the last vector in the transformed_matrix
        # The rest of the matrix is what we are comparing
        distances = self.metric.distances(transform_matrix[-1], transform_matrix[:-1])  

        # Get the indices of the top_k most similar (least distant) documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:top_k]
        return [self.documents[i] for i in top_k_indices]
