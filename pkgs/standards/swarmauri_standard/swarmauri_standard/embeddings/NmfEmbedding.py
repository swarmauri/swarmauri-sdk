import joblib
from typing import List, Any, Literal
from pydantic import PrivateAttr
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from swarmauri_base.embeddings.EmbeddingBase import EmbeddingBase
from swarmauri_standard.vectors.Vector import Vector

class NmfEmbedding(EmbeddingBase):
    n_components: int = 10
    _tfidf_vectorizer = PrivateAttr()
    _model = PrivateAttr()
    feature_names: List[Any] = []
    
    type: Literal['NmfEmbedding'] = 'NmfEmbedding'
    def __init__(self,**kwargs):

        super().__init__(**kwargs)
        # Initialize TF-IDF Vectorizer
        self._tfidf_vectorizer = TfidfVectorizer()
        # Initialize NMF with the desired number of components
        self._model = NMF(n_components=self.n_components)

    def fit(self, data):
        """
        Fit the NMF model to data.

        Args:
            data (Union[str, Any]): The text data to fit.
        """
        # Transform data into TF-IDF matrix
        tfidf_matrix = self._tfidf_vectorizer.fit_transform(data)
        # Fit the NMF model
        self._model.fit(tfidf_matrix)
        # Store feature names
        self.feature_names = self._tfidf_vectorizer.get_feature_names_out()

    def transform(self, data):
        """
        Transform new data into NMF feature space.

        Args:
            data (Union[str, Any]): Text data to transform.

        Returns:
            List[IVector]: A list of vectors representing the transformed data.
        """
        # Transform data into TF-IDF matrix
        tfidf_matrix = self._tfidf_vectorizer.transform(data)
        # Transform TF-IDF matrix into NMF space
        nmf_features = self._model.transform(tfidf_matrix)

        # Wrap NMF features in SimpleVector instances and return
        return [Vector(value=features.tolist()) for features in nmf_features]

    def fit_transform(self, data):
        """
        Fit the model to data and then transform it.
        
        Args:
            data (Union[str, Any]): The text data to fit and transform.

        Returns:
            List[IVector]: A list of vectors representing the fitted and transformed data.
        """
        self.fit(data)
        return self.transform(data)

    def infer_vector(self, data):
        """
        Convenience method for transforming a single data point.
        
        Args:
            data (Union[str, Any]): Single text data to transform.

        Returns:
            IVector: A vector representing the transformed single data point.
        """
        return self.transform([data])[0]
    
    def extract_features(self):
        """
        Extract the feature names from the TF-IDF vectorizer.
        
        Returns:
            The feature names.
        """
        return self.feature_names.tolist()

    def save_model(self, path: str) -> None:
        """
        Saves the NMF model and TF-IDF vectorizer using joblib.
        """
        # It might be necessary to save both tfidf_vectorizer and model
        # Consider using a directory for 'path' or appended identifiers for each model file
        joblib.dump(self._tfidf_vectorizer, f"{path}_tfidf.joblib")
        joblib.dump(self._model, f"{path}_nmf.joblib")

    def load_model(self, path: str) -> None:
        """
        Loads the NMF model and TF-IDF vectorizer from paths using joblib.
        """
        self._tfidf_vectorizer = joblib.load(f"{path}_tfidf.joblib")
        self._model = joblib.load(f"{path}_nmf.joblib")
        # Dependending on your implementation, you might need to refresh the feature_names
        self.feature_names = self._tfidf_vectorizer.get_feature_names_out()