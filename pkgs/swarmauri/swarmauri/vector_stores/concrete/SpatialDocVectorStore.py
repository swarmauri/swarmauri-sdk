from typing import List, Union, Literal
from swarmauri.documents.concrete.Document import Document
from swarmauri.embeddings.concrete.SpatialDocEmbedding import SpatialDocEmbedding
from swarmauri.distances.concrete.CosineDistance import CosineDistance

from swarmauri.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.vector_stores.base.VectorStoreRetrieveMixin import VectorStoreRetrieveMixin
from swarmauri.vector_stores.base.VectorStoreSaveLoadMixin import VectorStoreSaveLoadMixin    


class SpatialDocVectorStore(VectorStoreSaveLoadMixin, VectorStoreRetrieveMixin, VectorStoreBase):
    type: Literal['SpatialDocVectorStore'] = 'SpatialDocVectorStore'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._embedder = SpatialDocEmbedding()  # Assuming this is already implemented
        self._distance = CosineDistance()
        self.documents: List[Document] = []

    def add_document(self, document: Document) -> None:
        self.add_documents([document])  # Reuse the add_documents logic for batch processing

    def add_documents(self, documents: List[Document]) -> None:
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
        embeddings = self._embedder.vectorize_document(chunks, metadata_list=metadata_list)
        
        # Create Document instances for each document with the generated embeddings
        for doc, embedding in zip(documents, embeddings):
            embedded_doc = Document(
                id=doc.id, 
                content=doc.content, 
                metadata=doc.metadata, 
                embedding=embedding
            )
            self.documents.append(embedded_doc)

    def get_document(self, id: str) -> Union[Document, None]:
        for document in self.documents:
            if document.id == id:
                return document
        return None
        
    def get_all_documents(self) -> List[Document]:
        return self.documents

    def delete_document(self, id: str) -> None:
        self.documents = [_d for _d in self.documents if _d.id != id]

    def update_document(self, id: str) -> None:
        raise NotImplementedError('Update_document not implemented on SpatialDocVectorStore class.')
        
    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        query_vector = self._embedder.infer_vector(query)
        document_vectors = [_d.embedding for _d in self.documents if _d.content]
        distances = self._distance.distances(query_vector, document_vectors)
        
        # Get the indices of the top_k most similar documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:top_k]
        
        return [self.documents[i] for i in top_k_indices]

