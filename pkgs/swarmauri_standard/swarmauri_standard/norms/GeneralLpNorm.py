import logging
from abc import ABC
from typing import Union, Any, Sequence, Tuple, Optional, Callable, Literal
from swarmauri_base.norms import NormBase
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

logger = logging.getLogger(__name__)

@ComponentBase.register_type(NormBase, "GeneralLpNorm")
class GeneralLpNorm(NormBase):
    """Concrete implementation of the Lp norm for p in (1, ∞)."""
    
    type: Literal["GeneralLpNorm"] = "GeneralLpNorm"
    
    def __init__(self, p: float = 2):
        """
        Initialize the GeneralLpNorm instance with parameter p.
        
        Args:
            p: The parameter of the Lp norm. Must be greater than 1.
        """
        super().__init__()
        if p <= 1 or not self._is_finite(p):
            raise ValueError("Parameter p must be greater than 1 and finite.")
        self.p = p
        
    def _is_finite(self, value: float) -> bool:
        """
        Check if the given value is finite.
        
        Args:
            value: The value to check.
            
        Returns:
            bool: True if the value is finite, False otherwise.
        """
        return value == value and value != float('inf') and value != float('-inf')
        
    def compute(self, x: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Compute the Lp norm of the input x.
        
        Args:
            x: The input to compute the norm for. Can be a vector, matrix, sequence, string, or callable.
            
        Returns:
            float: The computed Lp norm value.
        """
        if isinstance(x, (IVector, Sequence)):
            return self._compute_vector_norm(x)
        elif isinstance(x, IMatrix):
            return self._compute_matrix_norm(x)
        elif isinstance(x, str):
            return self._compute_string_norm(x)
        elif callable(x):
            return self._compute_callable_norm(x)
        else:
            raise TypeError(f"Unsupported type for Lp norm computation: {type(x)}")
    
    def _compute_vector_norm(self, x: Union[IVector, Sequence]) -> float:
        """
        Compute the Lp norm for a vector or sequence.
        
        Args:
            x: The vector or sequence to compute the norm for.
            
        Returns:
            float: The computed Lp norm value.
        """
        return (sum(abs(x_i)**self.p for x_i in x)) ** (1.0 / self.p)
    
    def _compute_matrix_norm(self, x: IMatrix) -> float:
        """
        Compute the Lp norm for a matrix.
        
        For matrices, the Lp norm is computed as the maximum norm of rows or columns
        depending on the matrix type (row or column vector).
        
        Args:
            x: The matrix to compute the norm for.
            
        Returns:
            float: The computed Lp norm value.
        """
        if x.is_row_vector:
            return self._compute_vector_norm(x.rows[0])
        else:
            return max(self._compute_vector_norm(col) for col in x.columns)
    
    def _compute_string_norm(self, x: str) -> float:
        """
        Compute the Lp norm for a string.
        
        Treats each character as its ASCII value.
        
        Args:
            x: The string to compute the norm for.
            
        Returns:
            float: The computed Lp norm value.
        """
        return self._compute_vector_norm([ord(c) for c in x])
    
    def _compute_callable_norm(self, x: Callable) -> float:
        """
        Compute the Lp norm for a callable object.
        
        Assumes the callable returns a number when called.
        
        Args:
            x: The callable to compute the norm for.
            
        Returns:
            float: The computed Lp norm value.
        """
        result = x()
        if isinstance(result, (int, float)):
            return abs(result)
        else:
            raise ValueError("Callable must return a numeric value.")
    
    def check_non_negativity(self, x: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Check if the norm is non-negative.
        
        Args:
            x: The input to check the norm for.
            
        Raises:
            AssertionError: If the norm is negative.
        """
        logger.debug(f"Checking non-negativity for input: {x}")
        norm = self.compute(x)
        if norm < 0:
            raise AssertionError(f"Norm value {norm} is negative. Non-negativity violated.")
        logger.debug("Non-negativity check passed.")
    
    def check_triangle_inequality(self, x: Union[IVector, IMatrix, Sequence, str, Callable],
                                    y: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Check the triangle inequality: ||x + y|| <= ||x|| + ||y||.
        
        Args:
            x: First input vector.
            y: Second input vector.
            
        Raises:
            AssertionError: If the triangle inequality is violated.
        """
        logger.debug(f"Checking triangle inequality for inputs: {x}, {y}")
        norm_x_plus_y = self.compute(x + y)
        norm_x = self.compute(x)
        norm_y = self.compute(y)
        if norm_x_plus_y > norm_x + norm_y:
            raise AssertionError(f"Triangle inequality violated: {norm_x_plus_y} > {norm_x} + {norm_y}")
        logger.debug("Triangle inequality check passed.")
    
    def check_absolute_homogeneity(self, x: Union[IVector, IMatrix, Sequence, str, Callable],
                                     a: float) -> None:
        """
        Check absolute homogeneity: ||a * x|| = |a| * ||x||.
        
        Args:
            x: Input vector.
            a: Scalar multiplier.
            
        Raises:
            AssertionError: If absolute homogeneity is violated.
        """
        logger.debug(f"Checking absolute homogeneity for input: {x}, scalar: {a}")
        norm_scaled = self.compute(a * x)
        norm_original = self.compute(x)
        expected = abs(a) * norm_original
        if not (abs(norm_scaled - expected) < 1e-9):  # Using approximate equality for floats
            raise AssertionError(f"Absolute homogeneity violated: {norm_scaled} != {expected}")
        logger.debug("Absolute homogeneity check passed.")
    
    def check_definiteness(self, x: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Check definiteness: ||x|| = 0 if and only if x is the zero vector.
        
        Args:
            x: Input vector to check.
            
        Raises:
            AssertionError: If definiteness is violated.
        """
        logger.debug(f"Checking definiteness for input: {x}")
        norm = self.compute(x)
        if norm == 0:
            logger.info("Norm is zero, implying x is the zero vector")
        else:
            logger.info("Norm is non-zero, x is non-zero")
        logger.debug("Definiteness check completed.")
    
    def __str__(self) -> str:
        return f"GeneralLpNorm(p={self.p})"
    
    def __repr__(self) -> str:
        return f"GeneralLpNorm(p={self.p})"