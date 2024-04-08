import numpy as np
import scann
from typing import List, Dict, Union

from swarmauri.core.vector_stores.IVectorStore import IVectorStore
from swarmauri.core.vector_stores.ISimiliarityQuery import ISimilarityQuery
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector


class ScannVectorStore(IVectorStore, ISimilarityQuery):
    """
    A vector store that utilizes ScaNN (Scalable Nearest Neighbors) for efficient similarity searches.
    """

    def __init__(self, dimension: int, num_leaves: int = 100, num_leaves_to_search: int = 10, reordering_num_neighbors: int = 100):
        """
        Initialize the ScaNN vector store with given parameters.

        Parameters:
        - dimension (int): The dimensionality of the vectors being stored.
        - num_leaves (int): The number of leaves for the ScaNN partitioning tree.
        - num_leaves_to_search (int): The number of leaves to search for query time. Must be <= num_leaves.
        - reordering_num_neighbors (int): The number of neighbors to re-rank based on the exact distance after searching leaves.
        """
        self.dimension = dimension
        self.num_leaves = num_leaves
        self.num_leaves_to_search = num_leaves_to_search
        self.reordering_num_neighbors = reordering_num_neighbors

        self.searcher = None  # Placeholder for the ScaNN searcher initialized during building
        self.dataset_vectors = []
        self.id_to_metadata = {}

    def _build_scann_searcher(self):
        """Build the ScaNN searcher based on current dataset vectors."""
        self.searcher = scann.ScannBuilder(np.array(self.dataset_vectors, dtype=np.float32), num_neighbors=self.reordering_num_neighbors, distance_measure="dot_product").tree(
            num_leaves=self.num_leaves, num_leaves_to_search=self.num_leaves_to_search, training_sample_size=25000
        ).score_ah(
            dimensions_per_block=2
        ).reorder(self.reordering_num_neighbors).build()

    def add_vector(self, vector_id: str, vector: Union[np.ndarray, List[float]], metadata: Dict = None) -> None:
        """
        Adds a vector along with its identifier and optional metadata to the store.

        Args:
            vector_id (str): Unique identifier for the vector.
            vector (Union[np.ndarray, List[float]]): The high-dimensional vector to be stored.
            metadata (Dict, optional): Optional metadata related to the vector.
        """
        if not isinstance(vector, np.ndarray):
            vector = np.array(vector, dtype=np.float32)
        
        if self.searcher is None:
            self.dataset_vectors.append(vector)
        else:
            raise Exception("Cannot add vectors after building the index. Rebuild the index to include new vectors.")

        if metadata is None:
            metadata = {}
        self.id_to_metadata[vector_id] = metadata

    def build_index(self):
        """Builds or rebuilds the ScaNN searcher to reflect the current dataset vectors."""
        self._build_scann_searcher()

    def get_vector(self, vector_id: str) -> Union[IVector, None]:
        """
        Retrieve a vector by its identifier.

        Args:
            vector_id (str): The unique identifier for the vector.

        Returns:
            Union[IVector, None]: The vector associated with the given id, or None if not found.
        """
        if vector_id in self.id_to_metadata:
            metadata = self.id_to_metadata[vector_id]
            return SimpleVector(data=metadata.get('vector'), metadata=metadata)
        return None

    def delete_vector(self, vector_id: str) -> None:
        """
        Deletes a vector from the ScannVectorStore and marks the index for rebuilding.
        Note: For simplicity, this function assumes vectors are uniquely identifiable by their metadata.

        Args:
            vector_id (str): The unique identifier for the vector to be deleted.
        """
        if vector_id in self.id_to_metadata:
            # Identify index of the vector to be deleted
            vector = self.id_to_metadata[vector_id]['vector']
            index = self.dataset_vectors.index(vector)

            # Remove vector and its metadata
            del self.dataset_vectors[index]
            del self.id_to_metadata[vector_id]

            # Since vector order is important for matching ids, rebuild the searcher to reflect deletion
            self.searcher = None
        else:
            # Handle case where vector_id is not found
            print(f"Vector ID {vector_id} not found.")

    def update_vector(self, vector_id: str, new_vector: Union[np.ndarray, List[float]], new_metadata: Dict = None) -> None:
        """
        Updates an existing vector in the ScannVectorStore and marks the index for rebuilding.

        Args:
            vector_id (str): The unique identifier for the vector to be updated.
            new_vector (Union[np.ndarray, List[float]]): The updated vector.
            new_metadata (Dict, optional): Optional updated metadata for the vector.
        """
        # Ensure new_vector is numpy array for consistency
        if not isinstance(new_vector, np.ndarray):
            new_vector = np.array(new_vector, dtype=np.float32)

        if vector_id in self.id_to_metadata:
            # Update operation follows delete then add strategy because vector order matters in ScaNN
            self.delete_vector(vector_id)
            self.add_vector(vector_id, new_vector, new_metadata)
        else:
            # Handle case where vector_id is not found
            print(f"Vector ID {vector_id} not found.")



    def search_by_similarity_threshold(self, query_vector: Union[np.ndarray, List[float]], similarity_threshold: float, space_name: str = None) -> List[Dict]:
        """
        Search vectors exceeding a similarity threshold to a query vector within an optional vector space.

        Args:
            query_vector (Union[np.ndarray, List[float]]): The high-dimensional query vector.
            similarity_threshold (float): The similarity threshold for filtering results.
            space_name (str, optional): The name of the vector space to search within. Not used in this implementation.

        Returns:
            List[Dict]: A list of dictionaries with vector IDs, similarity scores, and optional metadata that meet the similarity threshold.
        """
        if not isinstance(query_vector, np.ndarray):
            query_vector = np.array(query_vector, dtype=np.float32)
        
        if self.searcher is None:
            self._build_scann_searcher()
        
        _, indices = self.searcher.search(query_vector, final_num_neighbors=self.reordering_num_neighbors)
        results = [{"id": str(idx), "metadata": self.id_to_metadata.get(str(idx), {})} for idx in indices if idx < similarity_threshold]
        return results