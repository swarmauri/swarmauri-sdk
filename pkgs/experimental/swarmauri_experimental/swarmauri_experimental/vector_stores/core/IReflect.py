from abc import ABC, abstractmethod
from typing import List

class IReflect(ABC):
    """
    Interface for reflecting a vector across a specified plane or axis.
    """

    @abstractmethod
    def reflect_vector(self, vector: List[float], normal: List[float]) -> List[float]:
        """
        Reflects a vector across a plane or axis defined by a normal vector.

        Parameters:
        - vector (List[float]): The vector to be reflected.
        - normal (List[float]): The normal vector of the plane across which the vector will be reflected.

        Returns:
        - List[float]: The reflected vector.
        """
        pass