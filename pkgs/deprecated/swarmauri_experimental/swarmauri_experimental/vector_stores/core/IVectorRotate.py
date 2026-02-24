from abc import ABC, abstractmethod
from typing import List

class IRotate(ABC):
    """
    Interface for rotating a vector.
    """
    
    @abstractmethod
    def rotate(self, vector: List[float], angle: float, axis: List[float] = None) -> List[float]:
        """
        Rotate the given vector by a specified angle around an axis (for 3D) or in a plane (for 2D).

        For 2D vectors, the axis parameter can be omitted.

        Args:
            vector (List[float]): The vector to rotate.
            angle (float): The angle of rotation in degrees.
            axis (List[float], optional): The axis of rotation (applicable in 3D).

        Returns:
            List[float]: The rotated vector.
        """
        pass
