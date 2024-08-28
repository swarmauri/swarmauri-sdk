import os
import json
import pickle
import tempfile
from typing import List, Union, Literal
from qdrant_client import QdrantClient, models

from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.embeddings.concrete.Doc2VecEmbedding import Doc2VecEmbedding
from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance

from swarmauri.standard.vector_stores.base.VectorStoreBase import VectorStoreBase
from swarmauri.standard.vector_stores.base.VectorStoreRetrieveMixin import VectorStoreRetrieveMixin
from swarmauri.standard.vector_stores.base.VectorStoreSaveLoadMixin import VectorStoreSaveLoadMixin    


class QdrantVectorStore(VectorStoreSaveLoadMixin, VectorStoreRetrieveMixin, VectorStoreBase):
    """
    QdrantVectorStore is a concrete implementation that integrates functionality
    for saving, loading, storing, and retrieving vector documents, leveraging Qdrant as the backend.
    """
    type: Literal['QdrantVectorStore'] = 'QdrantVectorStore'

    def __init__(self, url: str, api_key: str, collection_name: str, vector_size: int):
        self._embedder = Doc2VecEmbedding(vector_size=vector_size)
        self._distance = CosineDistance()
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = collection_name
        exists = self.client.collection_exists(collection_name)
        
        if not exists:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
            )   


    def add_document(self, document: Document) -> None:
        """
        Add a single document to the document store.
        
        Parameters:
            document (Document): The document to be added to the store.
        """
        try:
            embedding = document.embedding or self.vectorizer.fit_transform(document.content).data 
            self.client.upsert(self.collection_name, points=[
                models.PointStruct(
                    id=document.id,
                    vector=embedding,
                    payload=document.metadata
                )
            ])
            
        except:
            embedding = document.embedding or self.vectorizer.fit_transform(document.content).data 
            self.client.upsert(self.collection_name, points=[
                models.PointStruct(
                    id=document.id,
                    vector=embedding,
                    payload=document.metadata
                )
            ])
            
        

    def add_documents(self, documents: List[Document]) -> None:
        """
        Add multiple documents to the document store in a batch operation.
        
        Parameters:
            documents (List[Document]): A list of documents to be added to the store.
        """
        self.vectorizer.fit_transform([doc.content for doc in documents])
        points = [
            models.PointStruct(
                id=doc.id,
                vector=doc.embedding or self.vectorizer.infer_vector(doc.content).data,
                payload=doc.metadata
            ) for doc in documents
        ]
        self.client.upsert(self.collection_name, points=points)

    def get_document(self, id: str) -> Union[Document, None]:
        """
        Retrieve a single document by its identifier.
        
        Parameters:
            id (str): The unique identifier of the document to retrieve.
        
        Returns:
            Union[Document, None]: The requested document if found; otherwise, None.
        """
        
        raise NotImplementedError('Get document not implemented, use retrieve().')

    def get_all_documents(self) -> List[Document]:
        """
        Retrieve all documents stored in the document store.
        
        Returns:
            List[Document]: A list of all documents in the store.
        """
        raise NotImplementedError('Get all documents not implemented, use retrieve().')

    def delete_document(self, id: str) -> None:
        """
        Delete a document from the document store by its identifier.
        
        Parameters:
            id (str): The unique identifier of the document to delete.
        """
        self.client.delete(self.collection_name, points_selector=[id])

    def update_document(self, id: str, updated_document: Document) -> None:
        """
        Update a document in the document store.
        
        Parameters:
            id (str): The unique identifier of the document to update.
            updated_document (Document): The updated document instance.
        """
        self.client.upsert(self.collection_name, points=[                           
            models.PointStruct(
                id=updated_document.id,
                vector=updated_document.embedding,
                payload=updated_document.metadata
            )
        ])

    def clear_documents(self) -> None:
        """
        Deletes all documents from the vector store
        """
        self.documents = []
        self.client.delete(self.collection_name, points_selector=models.FilterSelector())

    def document_count(self) -> int:
        """
        Returns the number of documents in the store.
        """
        raise NotImplementedError('Get document not implemeneted, use retrieve().')

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        """
        Retrieve the top_k most relevant documents based on the given query.
        For the purpose of this example, this method performs a basic search.
        
        Args:
            query (str): The query string used for document retrieval. 
            top_k (int): The number of top relevant documents to retrieve.
        
        Returns:
            List[Document]: A list of the top_k most relevant documents.
        """
        # This should be modified to a query to the Qdrant service for relevance search
        query_vector = self.vectorizer.infer_vector(query).data
        documents = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k)
        
        matching_documents = [
            doc.payload for doc in documents
        ]
        return matching_documents[:top_k]
