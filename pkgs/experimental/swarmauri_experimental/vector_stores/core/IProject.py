from abc import ABC, abstractmethod
from typing import List

class IProject(ABC):
    """
    Interface for projecting one vector onto another.
    """

    @abstractmethod
    def project(self, vector_a: List[float], vector_b: List[float]) -> List[float]:
        """
        Projects vector_a onto vector_b.
        
        Args:
            vector_a (List[float]): The vector to be projected.
            vector_b (List[float]): The vector onto which vector_a is projected.
        
        Returns:
            List[float]: The projection of vector_a onto vector_b.
        """
        pass

