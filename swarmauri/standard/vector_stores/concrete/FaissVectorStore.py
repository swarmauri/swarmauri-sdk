import faiss
import numpy as np
from typing import List, Dict

from swarmauri.core.vector_stores.IVectorStore import IVectorStore
from swarmauri.core.vector_stores.ISimilarityQuery import ISimilarityQuery
from swarmauri.core.vectors.IVector import IVector

class FaissVectorStore(IVectorStore, ISimilarityQuery):
    """
    A vector store that utilizes FAISS for efficient similarity searches.
    """

    def __init__(self, dimension: int, index_type: str = "IVF256,Flat"):
        """
        Initialize the FAISS vector store with the given dimension and index type.

        Parameters:
        - dimension (int): The dimensionality of the vectors being stored.
        - index_type (str): The FAISS index type. Defaults to "IVF256,Flat" for an inverted file index.
        """
        self.dimension = dimension
        self.index = faiss.index_factory(dimension, index_type)
        self.id_to_vector = {}
        self.id_to_metadata = {}

    def add_vector(self, vector_id: str, vector: IVector, metadata: Dict = None) -> None:
        """
        Add a vector along with its identifier and optional metadata to the store.

        Parameters:
        - vector_id (str): Unique identifier for the vector.
        - vector (IVector): The high-dimensional vector to be stored.
        - metadata (Dict, optional): Optional metadata related to the vector.
        """
        # Ensure the vector is a numpy array and add it to the FAISS index
        np_vector = np.array(vector.data, dtype='float32').reshape(1, -1)
        self.index.add(np_vector)
        self.id_to_vector[vector_id] = vector
        if metadata:
            self.id_to_metadata[vector_id] = metadata

    def get_vector(self, vector_id: str) -> IVector:
        """
        Retrieve a vector by its identifier.

        Parameters:
        - vector_id (str): The unique identifier for the vector.

        Returns:
        - IVector: The vector associated with the given ID.
        """
        return self.id_to_vector.get(vector_id)

    def search_by_similarity_threshold(self, query_vector: List[float], similarity_threshold: float, space_name: str = None) -> List[Dict]:
        """
        Search vectors exceeding a similarity threshold to a query vector within an optional vector space.

        Parameters:
        - query_vector (List[float]): The high-dimensional query vector.
        - similarity_threshold (float): The similarity threshold for filtering results.

        Returns:
        - List[Dict]: A list of dictionaries with vector IDs, similarity scores, and optional metadata that meet the similarity threshold.
        """
        # FAISS requires numpy arrays in float32 for searches
        np_query_vector = np.array(query_vector, dtype='float32').reshape(1, -1)

        # Perform the search. FAISS returns distances, which can be converted to similarities.
        _, I = self.index.search(np_query_vector, k=self.index.ntotal)  # Searching the entire index
        results = []
        for idx in I[0]:
            vector_id = list(self.id_to_vector.keys())[idx]
            # Simulate a similarity score based on the FAISS distance metric (e.g., L2 distance for now).
            # Note: Depending on the index type and application, you might want to convert distances to actual similarities.
            results.append({"id": vector_id, "score": similarity_threshold, "metadata": self.id_to_metadata.get(vector_id)})

        return results