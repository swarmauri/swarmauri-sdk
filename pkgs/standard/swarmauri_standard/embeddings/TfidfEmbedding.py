from typing import List, Union, Any, Literal
import joblib
from pydantic import PrivateAttr
from sklearn.feature_extraction.text import TfidfVectorizer as SklearnTfidfVectorizer

from swarmauri_base.embeddings.EmbeddingBase import EmbeddingBase
from swarmauri_standard.vectors.Vector import Vector


class TfidfEmbedding(EmbeddingBase):
    _model = PrivateAttr()
    _fit_matrix = PrivateAttr()
    type: Literal["TfidfEmbedding"] = "TfidfEmbedding"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._model = SklearnTfidfVectorizer()

    def extract_features(self):
        return self._model.get_feature_names_out().tolist()

    def fit(self, documents: List[str]) -> None:
        self._fit_matrix = self._model.fit_transform(documents)

    def fit_transform(self, documents: List[str]) -> List[Vector]:
        self._fit_matrix = self._model.fit_transform(documents)
        # Convert the sparse matrix rows into Vector instances
        vectors = [
            Vector(value=vector.toarray().flatten()) for vector in self._fit_matrix
        ]
        return vectors

    def transform(self, data: Union[str, Any], documents: List[str]) -> List[Vector]:
        raise NotImplementedError("Transform not implemented on TFIDFVectorizer.")

    def infer_vector(self, data: str, documents: List[str]) -> Vector:
        documents.append(data)
        tmp_tfidf_matrix = self.fit_transform(documents)
        query_vector = tmp_tfidf_matrix[-1]
        return query_vector

    def save_model(self, path: str) -> None:
        """
        Saves the TF-IDF model to the specified path using joblib.
        """
        joblib.dump(self._model, path)

    def load_model(self, path: str) -> None:
        """
        Loads a TF-IDF model from the specified path using joblib.
        """
        self._model = joblib.load(path)
