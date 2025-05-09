from typing import Union, Optional, List, Tuple
import logging
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.seminorms.ISeminorm import ISeminorm
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class PartialSumSeminorm(SeminormBase):
    """
    A class providing implementation for computing seminorms on partial segments of vectors.

    Inherits from SeminormBase and implements the ISeminorm interface. This class
    computes the seminorm by summing only a specified part of the input vector.

    Attributes:
        _start_index: int - Starting index for partial sum (inclusive)
        _end_index: int - Ending index for partial sum (exclusive)
        resource: str - Resource type identifier

    Methods:
        compute: Computes the seminorm by summing elements from start_index to end_index
        check_triangle_inequality: Verifies the triangle inequality property
        check_scalar_homogeneity: Verifies the scalar homogeneity property
    """
    _start_index: int
    _end_index: int
    resource: str = ResourceTypes.SEMINORM.value

    def __init__(self, start_index: int = 0, end_index: int = None):
        """
        Initializes the PartialSumSeminorm instance.

        Args:
            start_index: Starting index for the partial sum (inclusive)
            end_index: Ending index for the partial sum (exclusive). If None, defaults to the end of the vector.
        """
        super().__init__()
        self._start_index = start_index
        self._end_index = end_index
        logger.debug(f"Initialized PartialSumSeminorm with start_index={start_index}, end_index={end_index}")

    def compute(self, input: Union[IVector, IMatrix, List[float], Tuple[float, ...], str, Callable]) -> float:
        """
        Computes the seminorm by summing the elements from start_index to end_index.

        Args:
            input: The input vector-like structure to compute the seminorm for.
                   Supported types: IVector, IMatrix, list, tuple, and others.

        Returns:
            float: The computed seminorm value

        Raises:
            ValueError: If indices are out of bounds
            TypeError: If input type is not supported
        """
        logger.debug(f"Computing partial sum seminorm for input of type {type(input).__name__}")
        
        if self._is_vector(input):
            vector = input.data()
        elif self._is_matrix(input):
            vector = input.data()[0]  # Assuming first row for matrices
        elif isinstance(input, (list, tuple)):
            vector = list(input)
        else:
            raise TypeError(f"Unsupported input type: {type(input).__name__}")

        # Validate indices
        if self._end_index is None:
            self._end_index = len(vector)
            
        if self._start_index >= len(vector):
            raise ValueError("Start index out of bounds")
        if self._end_index > len(vector):
            raise ValueError("End index out of bounds")

        # Compute partial sum
        return sum(vector[self._start_index:self._end_index])

    def check_triangle_inequality(self, a: Union[IVector, IMatrix, List[float], Tuple[float, ...]], 
                                  b: Union[IVector, IMatrix, List[float], Tuple[float, ...]]) -> bool:
        """
        Verifies the triangle inequality property: seminorm(a + b) <= seminorm(a) + seminorm(b).

        Args:
            a: First element to check
            b: Second element to check

        Returns:
            bool: True if triangle inequality holds, False otherwise
        """
        logger.debug("Checking triangle inequality for PartialSumSeminorm")
        
        seminorm_ab = self.compute(a + b)
        seminorm_a = self.compute(a)
        seminorm_b = self.compute(b)
        
        return seminorm_ab <= seminorm_a + seminorm_b

    def check_scalar_homogeneity(self, a: Union[IVector, IMatrix, List[float], Tuple[float, ...]], 
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
        
        scaled_a = a * scalar
        seminorm_scaled = self.compute(scaled_a)
        seminorm_original = self.compute(a)
        
        return seminorm_scaled == abs(scalar) * seminorm_original

    def __str__(self) -> str:
        """
        Returns a string representation of the PartialSumSeminorm instance.
        
        Returns:
            str: String representation
        """
        return f"PartialSumSeminorm(start_index={self._start_index}, end_index={self._end_index})"

    def __repr__(self) -> str:
        """
        Returns the official string representation of the PartialSumSeminorm instance.
        
        Returns:
            str: Official string representation
        """
        return self.__str__()