import logging
from abc import ABC
from typing import Union, TypeVar
import numpy as np

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.seminorms.SeminormBase import SeminormBase

T = TypeVar('T', np.ndarray, Union[np.ndarray, np.generic], str)

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SeminormBase, "TraceSeminorm")
class TraceSeminorm(SeminormBase):
    """
    A class that implements the trace seminorm functionality.

    This class provides the implementation for computing the trace seminorm of a matrix.
    The trace seminorm is defined as the absolute value of the trace of the matrix.
    The trace is the sum of the diagonal elements of the matrix. This implementation does not
    guarantee positive-definiteness of the matrix.

    Inherits from:
        SeminormBase: The base class for all seminorm implementations.

    Attributes:
        type: The type identifier for this seminorm implementation.
        resource: The resource type identifier for seminorm components.
    """
    type: str = "TraceSeminorm"
    resource: str = "SEMINORM"

    def __init__(self):
        """
        Initializes the TraceSeminorm class.
        
        Initializes the base class and sets up the logging.
        """
        super().__init__()
        logger.debug("TraceSeminorm class initialized")

    def compute(self, input: T) -> float:
        """
        Computes the trace seminorm of the input matrix.

        Args:
            input: T
                The input matrix for which to compute the trace seminorm.
                Must support the trace operation (e.g., numpy.ndarray).

        Returns:
            float:
                The computed trace seminorm value, which is the absolute value
                of the trace of the input matrix.

        Raises:
            ValueError:
                If the input does not support the trace operation.
            NotImplementedError:
                If the input type is not supported.
        """
        logger.debug("Computing trace seminorm")
        
        try:
            if isinstance(input, np.ndarray):
                trace = np.trace(input)
            elif hasattr(input, 'trace'):
                trace = input.trace()
            else:
                raise ValueError("Input must support trace operation")
            
            return abs(float(trace))
            
        except Exception as e:
            logger.error(f"Error computing trace seminorm: {str(e)}")
            raise ValueError("Failed to compute trace seminorm") from e

    def check_triangle_inequality(self, a: T, b: T) -> bool:
        """
        Checks if the triangle inequality holds for the trace seminorm.

        The triangle inequality states that:
        ||a + b|| <= ||a|| + ||b||

        For trace seminorm, this becomes:
        |trace(a + b)| <= |trace(a)| + |trace(b)|

        Args:
            a: T
                The first matrix
            b: T
                The second matrix

        Returns:
            bool:
                True if the triangle inequality holds, False otherwise
        """
        logger.debug("Checking triangle inequality")
        
        try:
            norm_a = self.compute(a)
            norm_b = self.compute(b)
            norm_a_plus_b = self.compute(a + b)
            
            return norm_a_plus_b <= norm_a + norm_b
            
        except Exception as e:
            logger.error(f"Error checking triangle inequality: {str(e)}")
            return False

    def check_scalar_homogeneity(self, a: T, scalar: float) -> bool:
        """
        Checks if the scalar homogeneity property holds for the trace seminorm.

        The scalar homogeneity property states that:
        ||s * a|| = |s| * ||a||

        For trace seminorm, this becomes:
        |trace(s * a)| = |s| * |trace(a)|

        Args:
            a: T
                The input matrix
            scalar: float
                The scalar to test homogeneity with

        Returns:
            bool:
                True if scalar homogeneity holds, False otherwise
        """
        logger.debug("Checking scalar homogeneity")
        
        try:
            norm_a = self.compute(a)
            norm_scaled_a = self.compute(scalar * a)
            
            return norm_scaled_a == abs(scalar) * norm_a
            
        except Exception as e:
            logger.error(f"Error checking scalar homogeneity: {str(e)}")
            return False