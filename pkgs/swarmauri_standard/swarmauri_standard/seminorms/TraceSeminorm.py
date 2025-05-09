from swarmauri_base.seminorms import SeminormBase
from typing import Union, List, Tuple, Callable, Optional
import logging
from swarmauri_core.vectors import IVector
from swarmauri_core.matrices import IMatrix

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SeminormBase, "TraceSeminorm")
class TraceSeminorm(SeminormBase):
    """
    Computes the trace of a matrix as a seminorm without guaranteeing positive-definiteness.

    This class implements the trace seminorm, which is based on the trace of a matrix.
    The trace is simply the sum of the diagonal elements of a matrix. This seminorm
    does not guarantee positive-definiteness since it can be zero for non-zero
    matrices (e.g., matrices with trace zero).

    Inherits from SeminormBase and implements the required methods for
    seminorm computation and property checking.
    """
    type: str = "TraceSeminorm"

    def __init__(self):
        """
        Initializes the TraceSeminorm instance.
        """
        super().__init__()
        logger.debug("Initialized TraceSeminorm")

    def compute(self, input: Union[IVector, IMatrix, str, Callable, List, Tuple]) -> float:
        """
        Computes the trace seminorm of the input.

        Args:
            input: The input to compute the trace seminorm for. Supported types are:
                - IVector: High-dimensional vector
                - IMatrix: Matrix structure
                - str: String input
                - Callable: Callable function
                - List: List of elements
                - Tuple: Tuple of elements

        Returns:
            float: The computed trace seminorm value

        Raises:
            TypeError: If input type is not supported
        """
        logger.debug(f"Computing trace seminorm for input of type {type(input).__name__}")

        # Handle IVector input
        if self._is_vector(input):
            return float(input.sum())
        
        # Handle IMatrix input
        elif self._is_matrix(input):
            return float(input.trace())
        
        # Handle string input by treating it as a vector of character values
        elif isinstance(input, str):
            if not input:
                return 0.0
            return float(sum(ord(c) for c in input))
        
        # Handle callable input by evaluating it
        elif self._is_callable(input):
            result = input()
            if self._is_vector(result):
                return float(result.sum())
            elif self._is_matrix(result):
                return float(result.trace())
            else:
                raise TypeError("Callable did not return a supported type")
        
        # Handle list or tuple input by treating it as a sequence of values
        elif self._is_sequence(input):
            if not input:
                return 0.0
            return float(sum(float(x) for x in input if isinstance(x, (int, float))))
        
        # Handle scalar values
        elif isinstance(input, (int, float)):
            return float(input)
        
        # Raise error for unsupported types
        raise TypeError(f"Unsupported input type: {type(input).__name__}")

    def check_triangle_inequality(self, a: Union[IVector, IMatrix, str, Callable, List, Tuple],
                                    b: Union[IVector, IMatrix, str, Callable, List, tuple]) -> bool:
        """
        Verifies the triangle inequality property: trace_seminorm(a + b) <= trace_seminorm(a) + trace_seminorm(b).

        Args:
            a: First element to check
            b: Second element to check

        Returns:
            bool: True if triangle inequality holds, False otherwise
        """
        logger.debug("Checking triangle inequality for trace seminorm")
        
        # Compute seminorms
        seminorm_a = self.compute(a)
        seminorm_b = self.compute(b)
        
        # Check if a + b is supported
        try:
            a_plus_b = a + b
        except TypeError:
            logger.warning("a and b cannot be added, skipping triangle inequality check")
            return False
        
        seminorm_a_plus_b = self.compute(a_plus_b)
        
        return seminorm_a_plus_b <= seminorm_a + seminorm_b

    def check_scalar_homogeneity(self, a: Union[IVector, IMatrix, str, Callable, List, Tuple],
                                scalar: Union[int, float]) -> bool:
        """
        Verifies the scalar homogeneity property: trace_seminorm(s * a) = |s| * trace_seminorm(a).

        Args:
            a: Element to check
            scalar: Scalar value to scale with

        Returns:
            bool: True if scalar homogeneity holds, False otherwise
        """
        logger.debug(f"Checking scalar homogeneity with scalar {scalar}")
        
        # Handle different types of a
        if self._is_vector(a):
            scaled_a = scalar * a
            return self.compute(scaled_a) == abs(scalar) * self.compute(a)
        
        elif self._is_matrix(a):
            scaled_a = scalar * a
            return self.compute(scaled_a) == abs(scalar) * self.compute(a)
        
        elif isinstance(a, (str, Callable, List, Tuple)):
            # For non-vector/matrix types, scalar homogeneity may not hold
            return False
            
        else:
            return False

    def __str__(self) -> str:
        """
        Returns a string representation of the trace seminorm instance.
        """
        return f"TraceSeminorm()"

    def __repr__(self) -> str:
        """
        Returns the official string representation of the trace seminorm instance.
        """
        return self.__str__()