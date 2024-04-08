from abc import ABC, abstractmethod
from typing import Any, Dict, List

class IVector(ABC):
    """
    Interface for a high-dimensional data vector. This interface defines the
    basic structure and operations for interacting with vectors in various applications,
    such as machine learning, information retrieval, and similarity search.
    """

    @property
    @abstractmethod
    def data(self) -> List[float]:
        """
        The high-dimensional data that the vector represents. It is typically a list of float values.
        """
        pass

