from typing import List, Union
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument
from swarmauri.standard.vectorizers.concrete.BERTEmbeddingVectorizer import BERTEmbeddingVectorizer
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vector_stores.base.VectorDocumentStoreRetrieveBase import VectorDocumentStoreRetrieveBase

class BERTVectorStore(VectorDocumentStoreRetrieveBase):
    def __init__(self):
        self.documents: List[EmbeddedDocument] = []
        self.vectorizer = BERTEmbeddingVectorizer()  # Assuming this is already implemented
        self.metric = CosineDistance()

    def add_document(self, document: IDocument) -> None:
        """
        Override: Now documents are expected to have labels for fine-tuning when added. 
        For unsupervised use-cases, labels can be ignored at the vectorizer level.
        """
        self.documents.append(document)
        documents_text = [doc.content for doc in self.documents]
        documents_labels = [doc.metadata['label'] for doc in self.documents]
        self.vectorizer.fit(documents_text, documents_labels)
        embeddings = self.vectorizer.infer_vector(document.content)

        embedded_document = EmbeddedDocument(doc_id=document.id, 
            content=document.content, 
            metadata=document.metadata, 
            embedding=embeddings)

        self.documents.append(embedded_document)

    def add_documents(self, documents: List[IDocument]) -> None:
        # Batch addition of documents with potential fine-tuning trigger
        self.documents.extend(documents)
        documents_text = [doc.content for doc in documents]
        documents_labels = [doc.metadata['label'] for doc in self.documents]
        self.vectorizer.fit(documents_text, documents_labels)

    def get_document(self, doc_id: str) -> Union[EmbeddedDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None
        
    def get_all_documents(self) -> List[EmbeddedDocument]:
        return self.documents

    def delete_document(self, doc_id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != doc_id]

    def update_document(self, doc_id: str) -> None:
        raise NotImplementedError('Update_document not implemented on BERTDocumentStore class.')
        
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        query_vector = self.vectorizer.infer_vector(query)
        document_vectors = [doc.embedding for doc in self.documents]
        distances = [self.metric.similarities(query_vector, document_vectors)]
        
        # Get the indices of the top_k most similar documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i], reverse=True)[:top_k]
        
        return [self.documents[i] for i in top_k_indices]
