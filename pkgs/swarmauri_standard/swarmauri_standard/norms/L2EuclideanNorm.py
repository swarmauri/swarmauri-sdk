import logging
from typing import Union, Any, Sequence
from swarmauri_base.norms import NormBase
from swarmauri_core.vectors import IVector
from swarmauri_core.matrices import IMatrix

logger = logging.getLogger(__name__)


class L2EuclideanNorm(NormBase):
    """
    Concrete implementation of the NormBase class for computing the L2 Euclidean norm.

    The L2 norm is computed as the square root of the sum of squares of the vector components.
    This class handles various input types including IVector, IMatrix, sequences, strings, and callables.
    """

    type: str = "L2EuclideanNorm"

    def __init__(self):
        """
        Initialize the L2EuclideanNorm instance.
        """
        super().__init__()

    def compute(self, x: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Compute the L2 Euclidean norm of the input.

        Args:
            x: The input to compute the norm for. Can be an IVector, IMatrix, Sequence, string, or callable.

        Returns:
            float: The computed L2 norm value.

        Raises:
            ValueError: If the input type is not supported.
        """
        logger.debug(f"Computing L2 norm for input: {x}")
        
        try:
            # Convert x to a list of elements
            if isinstance(x, (IVector, IMatrix)):
                elements = x.to_list()
            elif isinstance(x, Sequence):
                elements = list(x)
            elif isinstance(x, str):
                # Treat string as a sequence of characters' ASCII values
                elements = [ord(c) for c in x]
            elif callable(x):
                # Assume the callable returns a vector-like object
                result = x()
                if isinstance(result, (IVector, IMatrix, Sequence)):
                    elements = result.to_list() if isinstance(result, (IVector, IMatrix)) else list(result)
                else:
                    raise ValueError("Callable did not return a supported type.")
            else:
                raise ValueError(f"Unsupported input type: {type(x).__name__}")

            # Compute the sum of squares
            sum_squares = sum(element ** 2 for element in elements)
            norm = sum_squares ** 0.5

            logger.debug(f"L2 norm computed as: {norm}")
            return norm

        except Exception as e:
            logger.error(f"Error computing L2 norm: {str(e)}")
            raise

    def __str__(self) -> str:
        """
        Return a string representation of the L2EuclideanNorm instance.
        
        Returns:
            str: The string representation.
        """
        return f"L2EuclideanNorm()"

    def __repr__(self) -> str:
        """
        Return the string representation for the L2EuclideanNorm class.
        
        Returns:
            str: The string representation.
        """
        return f"L2EuclideanNorm()"