from typing import Union, Sequence, Callable, Optional, Literal
from abc import ABC
import numpy as np
import logging

from swarmauri_core.seminorms.ISeminorm import ISeminorm
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.seminorms.SeminormBase import SeminormBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SeminormBase, "TraceSeminorm")
class TraceSeminorm(SeminormBase):
    """Concrete implementation of SeminormBase for computing trace seminorm.
    
    This class provides the implementation for computing the trace seminorm of
    matrices. The trace seminorm is defined as the sum of the absolute values
    of the eigenvalues (trace). This implementation works with matrices that
    may not be positive-definite and handles various input types.
    """
    
    type: Literal["TraceSeminorm"] = "TraceSeminorm"
    
    def __init__(self) -> None:
        """Initialize the TraceSeminorm instance."""
        super().__init__()
        logger.debug("TraceSeminorm instance initialized")
    
    def compute(
        self,
        input: Union[IVector, IMatrix, Sequence, str, Callable]
    ) -> float:
        """Compute the trace seminorm of the given input.

        Args:
            input: The input to compute the seminorm for. Supported types are:
                - IVector: Compute the absolute value of the single element
                - IMatrix: Compute the trace as sum of diagonal elements
                - Sequence: Treat as vector and compute absolute values
                - str: Convert to matrix if possible
                - Callable: Convert to matrix if possible

        Returns:
            float: The computed trace seminorm value.

        Raises:
            ValueError: If the input type is not supported
            TypeError: If the input is of incorrect type
            RuntimeError: If trace computation fails
        """
        logger.debug("Computing trace seminorm")
        
        try:
            if isinstance(input, IMatrix):
                # For matrices, compute trace
                return self._compute_matrix_trace(input)
            elif isinstance(input, IVector):
                # For vectors, take absolute value of the single element
                return abs(input.get_element(0))
            elif isinstance(input, Sequence):
                # For sequences, treat as vector and compute L1 norm
                return float(np.sum([abs(x) for x in input]))
            elif isinstance(input, (str, Callable)):
                # Convert to matrix if possible
                matrix = self._convert_to_matrix(input)
                return self._compute_matrix_trace(matrix)
            else:
                raise TypeError(f"Unsupported input type: {type(input)}")
                
        except Exception as e:
            logger.error(f"Failed to compute trace seminorm: {str(e)}")
            raise RuntimeError(f"Trace computation failed: {str(e)}")
    
    def _compute_matrix_trace(self, matrix: IMatrix) -> float:
        """Helper method to compute trace for matrix input."""
        logger.debug("Computing matrix trace")
        try:
            if hasattr(matrix, "trace"):
                trace = matrix.trace()
            else:
                # Convert to numpy array and compute trace
                trace = np.trace(matrix.to_numpy())
            return float(abs(trace))
        except Exception as e:
            logger.error(f"Failed to compute matrix trace: {str(e)}")
            raise
    
    def _convert_to_matrix(self, input: Union[str, Callable]) -> IMatrix:
        """Helper method to convert input to matrix if possible."""
        logger.debug("Converting input to matrix")
        try:
            if isinstance(input, str):
                # Handle string input if possible
                # Assuming string represents a matrix
                if input.isdigit():
                    # Simple case: string of digits
                    return self._vector_to_matrix(int(input))
                else:
                    # More complex cases would need specific handling
                    raise NotImplementedError("String conversion not implemented")
            elif callable(input):
                # Call the function to get the matrix
                return input()
            else:
                raise TypeError("Unsupported input type for conversion")
        except Exception as e:
            logger.error(f"Failed to convert input to matrix: {str(e)}")
            raise
    
    def _vector_to_matrix(self, value: int) -> IMatrix:
        """Helper method to convert single value to matrix."""
        logger.debug("Converting single value to matrix")
        # Create a 1x1 matrix with the value
        return np.array([[value]], dtype=float)
    
    def check_triangle_inequality(
        self,
        a: Union[IVector, IMatrix, Sequence, str, Callable],
        b: Union[IVector, IMatrix, Sequence, str, Callable]
    ) -> bool:
        """Check if the triangle inequality holds for the given inputs.

        Args:
            a: First element to check
            b: Second element to check

        Returns:
            bool: True if ||a + b|| <= ||a|| + ||b||, False otherwise
        """
        logger.debug("Checking triangle inequality")
        try:
            norm_a = self.compute(a)
            norm_b = self.compute(b)
            a_plus_b = self._add_inputs(a, b)
            norm_a_plus_b = self.compute(a_plus_b)
            return norm_a_plus_b <= (norm_a + norm_b)
        except Exception as e:
            logger.error(f"Failed to check triangle inequality: {str(e)}")
            return False
    
    def _add_inputs(
        self,
        a: Union[IVector, IMatrix, Sequence, str, Callable],
        b: Union[IVector, IMatrix, Sequence, str, Callable]
    ) -> Union[IVector, IMatrix, Sequence]:
        """Helper method to add two inputs element-wise."""
        logger.debug("Adding inputs")
        try:
            if isinstance(a, (IMatrix, IVector)) and isinstance(b, (IMatrix, IVector)):
                return a + b
            elif isinstance(a, Sequence) and isinstance(b, Sequence):
                return [a[i] + b[i] for i in range(len(a))]
            else:
                raise TypeError("Unsupported type combination for addition")
        except Exception as e:
            logger.error(f"Failed to add inputs: {str(e)}")
            raise
    
    def check_scalar_homogeneity(
        self,
        input: Union[IVector, IMatrix, Sequence, str, Callable],
        scalar: float
    ) -> bool:
        """Check if the seminorm satisfies scalar homogeneity.

        Args:
            input: Input element to check
            scalar: Scalar to scale the input by

        Returns:
            bool: True if ||c * x|| == |c| * ||x||, False otherwise
        """
        logger.debug("Checking scalar homogeneity")
        try:
            scaled_input = self._scale_input(input, scalar)
            norm_input = self.compute(input)
            norm_scaled = self.compute(scaled_input)
            return np.isclose(norm_scaled, abs(scalar) * norm_input)
        except Exception as e:
            logger.error(f"Failed to check scalar homogeneity: {str(e)}")
            return False
    
    def _scale_input(
        self,
        input: Union[IVector, IMatrix, Sequence, str, Callable],
        scalar: float
    ) -> Union[IVector, IMatrix, Sequence]:
        """Helper method to scale the input by a scalar."""
        logger.debug("Scaling input")
        try:
            if isinstance(input, (IMatrix, IVector)):
                return scalar * input
            elif isinstance(input, Sequence):
                return [scalar * x for x in input]
            else:
                raise TypeError("Unsupported type for scaling")
        except Exception as e:
            logger.error(f"Failed to scale input: {str(e)}")
            raise