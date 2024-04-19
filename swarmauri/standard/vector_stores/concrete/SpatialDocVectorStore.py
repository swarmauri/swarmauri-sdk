from typing import List, Union
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument
from swarmauri.standard.vectorizers.concrete.SpatialDocVectorizer import SpatialDocVectorizer
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vector_stores.base.VectorDocumentStoreRetrieveBase import VectorDocumentStoreRetrieveBase
from swarmauri.standard.vector_stores.base.SaveLoadStoreBase import SaveLoadStoreBase    

class SpatialDocVectorStore(VectorDocumentStoreRetrieveBase, SaveLoadStoreBase):
    def __init__(self):
        self.vectorizer = SpatialDocVectorizer()  # Assuming this is already implemented
        self.metric = CosineDistance()
        self.documents: List[EmbeddedDocument] = []
        SaveLoadStoreBase.__init__(self, self.vectorizer, self.documents)      

    def add_document(self, document: IDocument) -> None:
        self.add_documents([document])  # Reuse the add_documents logic for batch processing

    def add_documents(self, documents: List[IDocument]) -> None:
        chunks = [doc.content for doc in documents]
        # Prepare a list of metadata dictionaries for each document based on the required special tokens
        metadata_list = [{ 
            'dir': doc.metadata.get('dir', ''),
            'type': doc.metadata.get('type', ''),
            'section': doc.metadata.get('section', ''),
            'path': doc.metadata.get('path', ''),
            'paragraph': doc.metadata.get('paragraph', ''),
            'subparagraph': doc.metadata.get('subparagraph', ''),
            'chapter': doc.metadata.get('chapter', ''),
            'title': doc.metadata.get('title', ''),
            'subsection': doc.metadata.get('subsection', ''),
        } for doc in documents]

        # Use vectorize_document to process all documents with their corresponding metadata
        embeddings = self.vectorizer.vectorize_document(chunks, metadata_list=metadata_list)
        
        # Create EmbeddedDocument instances for each document with the generated embeddings
        for doc, embedding in zip(documents, embeddings):
            embedded_doc = EmbeddedDocument(
                id=doc.id, 
                content=doc.content, 
                metadata=doc.metadata, 
                embedding=embedding
            )
            self.documents.append(embedded_doc)

    def get_document(self, doc_id: str) -> Union[EmbeddedDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None
        
    def get_all_documents(self) -> List[EmbeddedDocument]:
        return self.documents

    def delete_document(self, doc_id: str) -> None:
        self.documents = [_d for _d in self.documents if _d.id != doc_id]

    def update_document(self, doc_id: str) -> None:
        raise NotImplementedError('Update_document not implemented on SpatialDocVectorStore class.')
        
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        query_vector = self.vectorizer.infer_vector(query)
        document_vectors = [_d.embedding for _d in self.documents if _d.content]
        distances = self.metric.distances(query_vector, document_vectors)
        
        # Get the indices of the top_k most similar documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:top_k]
        
        return [self.documents[i] for i in top_k_indices]

