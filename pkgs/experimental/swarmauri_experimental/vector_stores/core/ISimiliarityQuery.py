from abc import ABC, abstractmethod
from typing import List, Dict

class ISimilarityQuery(ABC):
    
    @abstractmethod
    def search_by_similarity_threshold(self, query_vector: List[float], similarity_threshold: float, space_name: str = None) -> List[Dict]:
        """
        Search vectors exceeding a similarity threshold to a query vector within an optional vector space.

        Args:
            query_vector (List[float]): The high-dimensional query vector.
            similarity_threshold (float): The similarity threshold for filtering results.
            space_name (str, optional): The name of the vector space to search within.

        Returns:
            List[Dict]: A list of dictionaries with vector IDs, similarity scores, and optional metadata that meet the similarity threshold.
        """
        pass