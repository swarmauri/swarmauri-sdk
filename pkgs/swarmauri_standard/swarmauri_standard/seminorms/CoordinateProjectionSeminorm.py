from typing import Union, Optional, List
import logging
import numpy as np

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.seminorms import SeminormBase
from swarmauri_core.vectors.IVector import IVector

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SeminormBase, "CoordinateProjectionSeminorm")
class CoordinateProjectionSeminorm(SeminormBase):
    """
    A seminorm implementation that computes the seminorm by projecting onto a specified subset of coordinates.
    
    This class provides functionality to ignore certain components of the vector, potentially leading to a degenerate seminorm.
    
    Attributes:
        projection_indices: List[int] - The indices of the coordinates to project onto
    """
    def __init__(self, projection_indices: List[int] = None):
        """
        Initializes the CoordinateProjectionSeminorm instance with specified projection indices.
        
        Args:
            projection_indices: List[int] - Optional list of indices to project onto. If None, all coordinates are used.
        """
        super().__init__()
        self.projection_indices = projection_indices if projection_indices is not None else []
        logger.debug(f"Initialized CoordinateProjectionSeminorm with projection indices {self.projection_indices}")

    def compute(self, input: Union[IVector, str, Callable, list, tuple]) -> float:
        """
        Computes the seminorm value of the input by projecting onto the specified coordinates.
        
        Args:
            input: The input to compute the seminorm for. Currently supports IVector and other types are forwarded to base class.
            
        Returns:
            float: The computed seminorm value
            
        Raises:
            NotImplementedError: If input type is not supported
        """
        logger.debug(f"Computing seminorm for input of type {type(input).__name__}")
        
        if isinstance(input, IVector):
            if not self.projection_indices:
                # If no projection indices are specified, use all coordinates
                vector = input.data
            else:
                # Project the vector onto the specified coordinates
                vector = input.data[self.projection_indices]
            
            # Compute the L2 norm of the projected vector
            return np.linalg.norm(vector)
        
        # For other input types, defer to base class implementation
        return super().compute(input)

    def check_triangle_inequality(self, a: Union[IVector, str, Callable, list, tuple],
                                  b: Union[IVector, str, Callable, list, tuple]) -> bool:
        """
        Verifies the triangle inequality property: seminorm(a + b) <= seminorm(a) + seminorm(b).
        
        Args:
            a: First element to check
            b: Second element to check
            
        Returns:
            bool: True if triangle inequality holds, False otherwise
        """
        logger.debug("Checking triangle inequality")
        
        seminorm_a = self.compute(a)
        seminorm_b = self.compute(b)
        seminorm_a_plus_b = self.compute(a + b)
        
        return seminorm_a_plus_b <= seminorm_a + seminorm_b

    def check_scalar_homogeneity(self, a: Union[IVector, str, Callable, list, tuple],
                               scalar: Union[int, float]) -> bool:
        """
        Verifies the scalar homogeneity property: seminorm(s * a) = |s| * seminorm(a).
        
        Args:
            a: Element to check
            scalar: Scalar value to scale with
            
        Returns:
            bool: True if scalar homogeneity holds, False otherwise
        """
        logger.debug(f"Checking scalar homogeneity with scalar {scalar}")
        
        scaled_a = scalar * a
        seminorm_scaled = self.compute(scaled_a)
        seminorm_original = self.compute(a)
        
        return np.isclose(seminorm_scaled, abs(scalar) * seminorm_original)

    def __str__(self) -> str:
        """
        Returns a string representation of the CoordinateProjectionSeminorm instance.
        
        Returns:
            str: String representation
        """
        return f"CoordinateProjectionSeminorm(projection_indices={self.projection_indices})"

    def __repr__(self) -> str:
        """
        Returns the official string representation of the CoordinateProjectionSeminorm instance.
        
        Returns:
            str: Official string representation
        """
        return self.__str__()