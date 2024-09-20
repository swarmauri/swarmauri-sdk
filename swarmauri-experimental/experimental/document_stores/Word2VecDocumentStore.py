from typing import List, Union, Optional
import numpy as np
from gensim.models import Word2Vec
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore
from swarmauri.core.retrievers.IRetriever import IRetriever
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument
from swarmauri.standard.vector_stores.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
import gensim.downloader as api

class Word2VecDocumentStore(IDocumentStore, IRetriever):
    def __init__(self):
        """
        Initializes the Word2VecDocumentStore.

        Parameters:
        - word2vec_model_path (Optional[str]): File path to a pre-trained Word2Vec model. 
                                               Leave None to use Gensim's pre-trained model.
        - pre_trained (bool): If True, loads a pre-trained Word2Vec model. If False, an uninitialized model is used that requires further training.
        """
        self.model = Word2Vec(vector_size=100, window=5, min_count=1, workers=4)  # Example parameters; adjust as needed
        self.documents = []
        self.metric = CosineDistance()

    def add_document(self, document: EmbeddedDocument) -> None:
        # Check if the document already has an embedding, if not generate one using _average_word_vectors
        if not hasattr(document, 'embedding') or document.embedding is None:
            words = document.content.split()  # Simple tokenization, consider using a better tokenizer
            embedding = self._average_word_vectors(words)
            document.embedding = embedding
            print(document.embedding)
        self.documents.append(document)
        
    def add_documents(self, documents: List[EmbeddedDocument]) -> None:
        self.documents.extend(documents)
        
    def get_document(self, doc_id: str) -> Union[EmbeddedDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None
        
    def get_all_documents(self) -> List[EmbeddedDocument]:
        return self.documents
        
    def delete_document(self, doc_id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != doc_id]

    def update_document(self, doc_id: str, updated_document: EmbeddedDocument) -> None:
        for i, document in enumerate(self.documents):
            if document.id == doc_id:
                self.documents[i] = updated_document
                break

    def _average_word_vectors(self, words: List[str]) -> np.ndarray:
        """
        Generate document vector by averaging its word vectors.
        """
        word_vectors = [self.model.wv[word] for word in words if word in self.model.wv]
        print(word_vectors)
        if word_vectors:
            return np.mean(word_vectors, axis=0)
        else:
            return np.zeros(self.model.vector_size)

    def retrieve(self, query: str, top_k: int = 5) -> List[EmbeddedDocument]:
        """
        Retrieve documents similar to the query string based on Word2Vec embeddings.
        """
        query_vector = self._average_word_vectors(query.split())
        print('query_vector', query_vector)
        # Compute similarity scores between the query and each document's stored embedding
        similarities = self.metric.similarities(SimpleVector(query_vector), [SimpleVector(doc.embedding) for doc in self.documents if doc.embedding])
        print('similarities', similarities)
        # Retrieve indices of top_k most similar documents
        top_k_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_k]
        print('top_k_indices', top_k_indices)
        return [self.documents[i] for i in top_k_indices]