from typing import TypeVar, Union
import math
import logging
from swarmauri_base.norms import NormBase

T = TypeVar('T', list[float], tuple[float], Union[float])

logger = logging.getLogger(__name__)


class L2EuclideanNorm(NormBase):
    """
    A class implementing the L2 Euclidean norm computation for real-valued vectors.

    Inherits from:
        NormBase: Base class providing template logic for norm computations.

    Attributes:
        type: String identifier for the norm type.

    Methods:
        compute: Computes the L2 Euclidean norm of a vector.
    """
    type: str = "L2EuclideanNorm"

    def compute(self, x: T) -> float:
        """
        Computes the Euclidean (L2) norm of a real-valued vector.

        The Euclidean norm is computed as the square root of the sum of
        the squares of the vector components.

        Args:
            x: Real-valued vector represented as a list or tuple of floats.

        Returns:
            float: The computed L2 norm value.

        Raises:
            TypeError: If the input type is not supported.
        """
        logger.debug("Computing L2 Euclidean norm")
        
        # Ensure input is a list or tuple of floats
        if not isinstance(x, (list, tuple)):
            raise TypeError("Input must be a list or tuple of floats")
            
        try:
            # Compute the sum of squares of vector components
            squared_sum = sum(element ** 2 for element in x)
            
            # Compute the square root of the sum
            norm = math.sqrt(squared_sum)
            
            return norm
            
        except TypeError as e:
            logger.error(f"Error computing norm: {str(e)}")
            raise TypeError("Vector elements must support element-wise squaring")
            
    def __str__(self) -> str:
        """
        Returns a string representation of the L2EuclideanNorm instance.
        """
        return f"L2EuclideanNorm()"

    def __repr__(self) -> str:
        """
        Returns a string representation of the L2EuclideanNorm instance.
        """
        return f"L2EuclideanNorm()"