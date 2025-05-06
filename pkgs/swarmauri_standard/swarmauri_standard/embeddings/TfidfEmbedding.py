from typing import List, Literal
import joblib
import math
from collections import Counter, defaultdict
from pydantic import PrivateAttr

from swarmauri_base.embeddings.EmbeddingBase import EmbeddingBase
from swarmauri_standard.vectors.Vector import Vector
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(EmbeddingBase, "TfidfEmbedding")
class TfidfEmbedding(EmbeddingBase):
    # Private attributes to store our custom model data.
    _fit_matrix = PrivateAttr()
    _features = PrivateAttr()  # Sorted list of vocabulary terms.
    _idf = PrivateAttr()  # Dict mapping term -> idf value.

    type: Literal["TfidfEmbedding"] = "TfidfEmbedding"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize our internal attributes.
        self._features = []  # This will hold our vocabulary.
        self._idf = {}  # This will hold the computed idf for each token.
        self._fit_matrix = []  # This will hold the TF-IDF vectors.

    def extract_features(self) -> List[str]:
        """
        Returns the list of features (vocabulary terms) that were extracted during fitting.
        """
        return self._features

    def fit(self, documents: List[str]) -> None:
        """
        Fits the TF-IDF model on the provided documents.
        It computes the vocabulary, document frequencies, idf values, and the TF-IDF
        vectors for each document.
        """
        N = len(documents)
        df = defaultdict(int)
        tokenized_docs = []

        # Tokenize documents and compute document frequency for each token.
        for doc in documents:
            # Simple tokenization: lowercasing and splitting on whitespace.
            tokens = doc.lower().split()
            tokenized_docs.append(tokens)
            for token in set(tokens):  # use set() to count each token once per doc
                df[token] += 1

        # Build a sorted vocabulary for consistent vector ordering.
        self._features = sorted(list(df.keys()))

        # Compute idf for each term using the formula: log(N / df)
        self._idf = {token: math.log(N / df[token]) for token in self._features}

        # Now compute the TF-IDF vector for each document.
        self._fit_matrix = []
        for tokens in tokenized_docs:
            tf = Counter(tokens)
            doc_len = len(tokens)
            vector = []
            for token in self._features:
                # Compute term frequency (TF) for the token in this document.
                tf_value = tf[token] / doc_len if doc_len > 0 else 0.0
                # Multiply by idf to get the TF-IDF weight.
                tfidf_value = tf_value * self._idf[token]
                vector.append(tfidf_value)
            self._fit_matrix.append(vector)

    def fit_transform(self, documents: List[str]) -> List[Vector]:
        """
        Fits the model on the provided documents and returns the TF-IDF vectors as a list
        of Vector instances.
        """
        self.fit(documents)
        return [Vector(value=vec) for vec in self._fit_matrix]

    def transform(self, documents: List[str]) -> List[Vector]:
        """
        Transforms new documents into TF-IDF vectors using the vocabulary and idf values
        computed during fitting. Any term not in the vocabulary is ignored.
        """
        if not self._features or not self._idf:
            raise ValueError(
                "The model has not been fitted yet. Please call fit first."
            )

        transformed_vectors = []
        for doc in documents:
            tokens = doc.lower().split()
            tf = Counter(tokens)
            doc_len = len(tokens)
            vector = []
            for token in self._features:
                tf_value = tf[token] / doc_len if doc_len > 0 else 0.0
                # If the token is not in the fitted vocabulary, its idf defaults to 0.
                idf_value = self._idf.get(token, 0.0)
                vector.append(tf_value * idf_value)
            transformed_vectors.append(Vector(value=vector))
        return transformed_vectors

    def infer_vector(self, data: str, documents: List[str]) -> Vector:
        """
        Infers a TF-IDF vector for a new document. In this implementation, we append the
        new document to the provided corpus, re-fit the model, and return the vector for
        the new document. (Note: This re-fits the model which might be inefficient for
        production but mirrors the original logic.)
        """
        documents.append(data)
        vectors = self.fit_transform(documents)
        return vectors[-1]

    def save_model(self, path: str) -> None:
        """
        Saves the TF-IDF model (i.e. the vocabulary and idf values) to the specified path
        using joblib.
        """
        model_data = {
            "features": self._features,
            "idf": self._idf,
        }
        joblib.dump(model_data, path)

    def load_model(self, path: str) -> None:
        """
        Loads a TF-IDF model (i.e. the vocabulary and idf values) from the specified path
        using joblib.
        """
        model_data = joblib.load(path)
        self._features = model_data.get("features", [])
        self._idf = model_data.get("idf", {})
