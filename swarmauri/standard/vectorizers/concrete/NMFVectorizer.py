import joblib

from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer

from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectorizers.IFeature import IFeature
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
from swarmauri.core.vectorizers.ISaveModel import ISaveModel

class NMFVectorizer(IVectorize, IFeature, ISaveModel):
    def __init__(self, n_components=10):
        # Initialize TF-IDF Vectorizer
        self.tfidf_vectorizer = TfidfVectorizer()
        # Initialize NMF with the desired number of components
        self.model = NMF(n_components=n_components)
        self.feature_names = []

    def fit(self, data):
        """
        Fit the NMF model to data.

        Args:
            data (Union[str, Any]): The text data to fit.
        """
        # Transform data into TF-IDF matrix
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(data)
        # Fit the NMF model
        self.model.fit(tfidf_matrix)
        # Store feature names
        self.feature_names = self.tfidf_vectorizer.get_feature_names_out()

    def transform(self, data):
        """
        Transform new data into NMF feature space.

        Args:
            data (Union[str, Any]): Text data to transform.

        Returns:
            List[IVector]: A list of vectors representing the transformed data.
        """
        # Transform data into TF-IDF matrix
        tfidf_matrix = self.tfidf_vectorizer.transform(data)
        # Transform TF-IDF matrix into NMF space
        nmf_features = self.model.transform(tfidf_matrix)

        # Wrap NMF features in SimpleVector instances and return
        return [SimpleVector(features.tolist()) for features in nmf_features]

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
        return self.feature_names

    def save_model(self, path: str) -> None:
        """
        Saves the NMF model and TF-IDF vectorizer using joblib.
        """
        # It might be necessary to save both tfidf_vectorizer and model
        # Consider using a directory for 'path' or appended identifiers for each model file
        joblib.dump(self.tfidf_vectorizer, f"{path}_tfidf.joblib")
        joblib.dump(self.model, f"{path}_nmf.joblib")

    def load_model(self, path: str) -> None:
        """
        Loads the NMF model and TF-IDF vectorizer from paths using joblib.
        """
        self.tfidf_vectorizer = joblib.load(f"{path}_tfidf.joblib")
        self.model = joblib.load(f"{path}_nmf.joblib")
        # Dependending on your implementation, you might need to refresh the feature_names
        self.feature_names = self.tfidf_vectorizer.get_feature_names_out()