import logging
import numpy as np
from typing import Any, Optional, Literal, Union, TypeVar
from numpy.typing import ArrayLike

from swarmauri_core.seminorms.ISeminorm import ISeminorm
from swarmauri_base.seminorms.SeminormBase import SeminormBase
from swarmauri_base.ComponentBase import ComponentBase

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for matrix-like objects
T = TypeVar('T', bound=ArrayLike)

@ComponentBase.register_type(SeminormBase, "TraceSeminorm")
class TraceSeminorm(SeminormBase[T]):
    """
    Implements a seminorm based on the trace of a matrix.
    
    This seminorm computes the trace of a matrix, which is the sum of the elements on the main diagonal.
    Note that this is not guaranteed to be positive-definite, so it may be a degenerate seminorm
    for some matrices.
    
    Attributes
    ----------
    type : Literal["TraceSeminorm"]
        The type identifier for this seminorm.
    """
    
    type: Literal["TraceSeminorm"] = "TraceSeminorm"
    
    def __init__(self):
        """Initialize the TraceSeminorm."""
        super().__init__()
        logger.debug("Initialized TraceSeminorm")
    
    def evaluate(self, x: T) -> float:
        """
        Evaluate the trace-based seminorm for a given matrix.
        
        Parameters
        ----------
        x : T
            The matrix to evaluate the seminorm on.
            
        Returns
        -------
        float
            The absolute value of the trace of the matrix.
            
        Raises
        ------
        ValueError
            If the input is not a square matrix or doesn't support the trace operation.
        """
        logger.debug("Evaluating trace seminorm")
        try:
            # Convert to numpy array if not already
            x_array = np.array(x)
            
            # Check if it's a square matrix
            if x_array.ndim != 2 or x_array.shape[0] != x_array.shape[1]:
                raise ValueError("Input must be a square matrix")
            
            # Compute the trace (sum of diagonal elements)
            trace_value = np.trace(x_array)
            
            # Return absolute value to ensure non-negativity
            return abs(trace_value)
        except Exception as e:
            logger.error(f"Error evaluating trace seminorm: {e}")
            raise ValueError(f"Failed to compute trace: {e}")
    
    def scale(self, x: T, alpha: float) -> float:
        """
        Evaluate the seminorm of a scaled matrix.
        
        Parameters
        ----------
        x : T
            The matrix to evaluate the seminorm on.
        alpha : float
            The scaling factor.
            
        Returns
        -------
        float
            The seminorm value of the scaled matrix.
        """
        logger.debug(f"Scaling trace seminorm by factor {alpha}")
        # For trace seminorm, p(αx) = |α|p(x)
        return abs(alpha) * self.evaluate(x)
    
    def triangle_inequality(self, x: T, y: T) -> bool:
        """
        Verify that the triangle inequality holds for the given matrices.
        
        Parameters
        ----------
        x : T
            First matrix.
        y : T
            Second matrix.
            
        Returns
        -------
        bool
            True if the triangle inequality holds, False otherwise.
        """
        logger.debug("Checking triangle inequality for trace seminorm")
        try:
            # Convert to numpy arrays
            x_array = np.array(x)
            y_array = np.array(y)
            
            # Check dimensions match
            if x_array.shape != y_array.shape:
                raise ValueError("Matrices must have the same dimensions")
            
            # Compute sum matrix
            sum_matrix = x_array + y_array
            
            # Check triangle inequality: p(x + y) <= p(x) + p(y)
            left_side = self.evaluate(sum_matrix)
            right_side = self.evaluate(x_array) + self.evaluate(y_array)
            
            return left_side <= right_side + 1e-10  # Add small tolerance for floating-point errors
        except Exception as e:
            logger.error(f"Error checking triangle inequality: {e}")
            raise
    
    def is_zero(self, x: T, tolerance: float = 1e-10) -> bool:
        """
        Check if the seminorm evaluates to zero (within a tolerance).
        
        Parameters
        ----------
        x : T
            The matrix to check.
        tolerance : float, optional
            The numerical tolerance for considering a value as zero.
            
        Returns
        -------
        bool
            True if the seminorm of x is zero (within tolerance), False otherwise.
        """
        logger.debug(f"Checking if trace seminorm is zero with tolerance {tolerance}")
        return self.evaluate(x) < tolerance
    
    def is_definite(self) -> bool:
        """
        Check if this seminorm is actually a norm (i.e., it has the definiteness property).
        
        The trace seminorm is not generally definite because there exist non-zero matrices
        with zero trace (e.g., traceless matrices).
        
        Returns
        -------
        bool
            False, as the trace seminorm is not definite.
        """
        logger.debug("Checking if trace seminorm is definite")
        # The trace seminorm is not definite because there are non-zero matrices with trace zero
        return False