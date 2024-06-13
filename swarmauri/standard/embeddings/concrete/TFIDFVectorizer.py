from typing import List, Union, Any
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer as SklearnTfidfVectorizer
from swarmauri.core.embeddings.IVectorize import IVectorize
from swarmauri.core.embeddings.IFeature import IFeature
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.Vector import Vector
from swarmauri.core.embeddings.ISaveModel import ISaveModel


class TFIDFVectorizer(IVectorize, IFeature, ISaveModel):
    def __init__(self):
        # Using scikit-learn's TfidfVectorizer as the underlying mechanism
        self.model = SklearnTfidfVectorizer()
        super().__init__()
        
    def extract_features(self):
        return self.model.get_feature_names_out()

    def fit(self, data: Union[str, Any]) -> List[IVector]:
        """
        Vectorizes the input data using the TF-IDF scheme.

        Parameters:
        - data (Union[str, Any]): The input data to be vectorized. Expected to be a single string (document)
                                  or a list of strings (corpus).

        Returns:
        - List[IVector]: A list containing IVector instances, each representing a document's TF-IDF vector.
        """
        if isinstance(data, str):
            data = [data]  # Convert a single string into a list for the vectorizer
        
        self.fit_matrix = self.model.fit_transform(data)

        # Convert the sparse matrix rows into Vector instances
        vectors = [Vector(vector.toarray().flatten()) for vector in self.fit_matrix]

        return vectors

    def fit_transform(self, data: Union[str, Any], documents) -> List[IVector]:
        documents = [doc.content for doc in documents]
        if isinstance(data, str):
            data = [data]  # Convert a single string into a list for the vectorizer
        documents.extend(data)

        transform_matrix = self.model.fit_transform(documents)

        # Convert the sparse matrix rows into Vector instances
        vectors = [Vector(vector.toarray().flatten()) for vector in transform_matrix]
        return vectors
    
    def transform(self, data: Union[str, Any], documents) -> List[IVector]:
        raise NotImplementedError('Transform not implemented on TFIDFVectorizer.')

    def infer_vector(self, data: str, documents) -> IVector:
        documents = [doc.content for doc in documents]
        documents.append(data)
        tmp_tfidf_matrix = self.transform(documents)
        query_vector = tmp_tfidf_matrix[-1]
        return query_vector

    def save_model(self, path: str) -> None:
        """
        Saves the TF-IDF model to the specified path using joblib.
        """
        joblib.dump(self.model, path)
    
    def load_model(self, path: str) -> None:
        """
        Loads a TF-IDF model from the specified path using joblib.
        """
        self.model = joblib.load(path)