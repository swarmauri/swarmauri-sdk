import math
import numpy as np
from collections import Counter
from typing import List, Union, Dict
from swarmauri.documents.concrete.Document import Document
from swarmauri.vector_stores.base.VectorStoreBase import VectorStoreBase

class BM25FVectorStore(VectorStoreBase):
    def __init__(self, vector_size, **kwargs):
        super().__init__(**kwargs)
        self.documents = []
        self.vectors = []  # Store document vectors in-memory
        self.vector_size = vector_size
        self.corpus_size = 0
        self.avg_doc_len = 0.0
        self.inverted_index = {}
        
        # BM25F parameters
        self.wf = {'content': 1.0}  # Weight for the field
        self.k1f = {'content': 1.5}  # Saturation control
        self.bf = {'content': 0.75}  # Length normalization
        self.idf_cache = {}

    def _calculate_avg_doc_len(self) -> float:
        total_length = sum(len(doc.content.split()) for doc in self.documents)
        return total_length / self.corpus_size if self.corpus_size > 0 else 0.0

    def _text_to_vector(self, text: str) -> np.ndarray:
        # Dummy vectorization; replace with actual embedding logic
        return np.random.rand(self.vector_size).astype('float32')

    def _build_inverted_index(self) -> None:
        self.inverted_index.clear()
        for idx, document in enumerate(self.documents):
            for term in document.content.split():
                if term not in self.inverted_index:
                    self.inverted_index[term] = []
                self.inverted_index[term].append(idx)

    def _idf(self, term: str) -> float:
        if term in self.idf_cache:
            return self.idf_cache[term]

        containing_docs = len(self.inverted_index.get(term, []))
        idf_value = math.log(
            (self.corpus_size - containing_docs + 0.5) / (containing_docs + 0.5) + 1
        )
        self.idf_cache[term] = idf_value
        return idf_value

    def _term_frequency(self, term: str, document: Document) -> int:
        term_count = Counter(document.content.split())
        return term_count.get(term, 0)

    def _bm25f_score(self, query: str, document: Document) -> float:
        score = 0.0
        query_terms = query.split()
        doc_length = len(document.content.split())

        for term in query_terms:
            idf = self._idf(term)
            for field_name in self.wf:
                f_weight = self.wf[field_name]
                k1 = self.k1f[field_name]
                b = self.bf[field_name]

                term_freq = self._term_frequency(term, document)
                length_norm = (1 - b + b * (doc_length / self.avg_doc_len))

                tf_component = (
                    f_weight * (term_freq * (k1 + 1)) /
                    (term_freq + k1 * length_norm)
                )
                score += idf * tf_component

        return score

    def _index_document(self, document: Document):
        content_vector = self._text_to_vector(document.content)
        self.vectors.append(content_vector)

    def add_document(self, document: Document) -> None:
        self.documents.append(document)
        self.corpus_size += 1
        self.avg_doc_len = self._calculate_avg_doc_len()
        self._build_inverted_index()
        self._index_document(document)

    def add_documents(self, documents: List[Document]) -> None:
        for doc in documents:
            self.add_document(doc)

    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        ranked_documents = sorted(
            self.documents,
            key=lambda doc: self._bm25f_score(query, doc),
            reverse=True
        )
        return ranked_documents[:top_k]

    def get_document(self, id: str) -> Union[Document, None]:
        for doc in self.documents:
            if doc.id == id:
                return doc
        return None

    def delete_document(self, id: str) -> None:
        index_to_remove = None
        for idx, doc in enumerate(self.documents):
            if doc.id == id:
                index_to_remove = idx
                break
        if index_to_remove is not None:
            del self.documents[index_to_remove]
            del self.vectors[index_to_remove]
            self.corpus_size = len(self.documents)
            self.avg_doc_len = self._calculate_avg_doc_len()
            self._build_inverted_index()

    def get_all_documents(self) -> List[Document]:
        return self.documents

    def update_document(self, id: str, document: Document) -> None:
        self.delete_document(id)
        self.add_document(document)

    def clear_documents(self) -> None:
        self.documents = []
        self.vectors = []
        self.corpus_size = 0
        self.avg_doc_len = 0.0
        self.inverted_index = {}
