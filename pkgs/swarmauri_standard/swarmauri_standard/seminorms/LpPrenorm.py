import logging
import numpy as np
from typing import Any, TypeVar, Literal, Optional, Union
import numpy.typing as npt

from swarmauri_base.seminorms.SeminormBase import SeminormBase
from swarmauri_core.ComponentBase import ComponentBase

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for generic typing
T = TypeVar('T', bound=Union[npt.NDArray[np.float64], list, tuple])

@ComponentBase.register_type(SeminormBase, "LpPrenorm")
class LpPrenorm(SeminormBase[T]):
    """
    Non-point-separating variant of Lp norm.
    
    This class implements a seminorm that computes an Lp-like measure on vectors
    but might not distinguish all vectors (hence "pre-norm"). Unlike a true norm,
    this seminorm may evaluate to zero for non-zero vectors.
    
    The Lp prenorm is defined as:
    ||x||_p = (sum(|x_i|^p))^(1/p) for p in (0, ∞)
    
    Attributes
    ----------
    type : Literal["LpPrenorm"]
        The type identifier for this component.
    p : float
        The p-value for the Lp prenorm calculation, must be in (0, ∞).
    """
    
    type: Literal["LpPrenorm"] = "LpPrenorm"
    p: float
    
    def __init__(self, p: float = 2.0):
        """
        Initialize the LpPrenorm with a specified p value.
        
        Parameters
        ----------
        p : float, optional
            The p-value for the Lp prenorm calculation, must be in (0, ∞).
            Default is 2.0 (Euclidean norm).
            
        Raises
        ------
        ValueError
            If p is not in the valid range (0, ∞).
        """
        super().__init__()
        if p <= 0:
            raise ValueError(f"p must be positive, got {p}")
        self.p = p
        logger.debug(f"Initialized LpPrenorm with p={p}")
    
    def evaluate(self, x: T) -> float:
        """
        Evaluate the Lp prenorm for a given input.
        
        Parameters
        ----------
        x : T
            The input vector to evaluate the prenorm on.
            
        Returns
        -------
        float
            The Lp prenorm value, which is non-negative.
        """
        logger.debug("Evaluating Lp prenorm")
        
        # Convert input to numpy array if it's not already
        if not isinstance(x, np.ndarray):
            x = np.array(x, dtype=float)
        
        # Handle empty array case
        if x.size == 0:
            return 0.0
        
        # Calculate the Lp prenorm
        return float(np.sum(np.abs(x) ** self.p) ** (1.0 / self.p))
    
    def scale(self, x: T, alpha: float) -> float:
        """
        Evaluate the prenorm of a scaled input.
        
        This method satisfies scalar homogeneity: p(αx) = |α|p(x)
        
        Parameters
        ----------
        x : T
            The input vector to evaluate the prenorm on.
        alpha : float
            The scaling factor.
            
        Returns
        -------
        float
            The prenorm value of the scaled input.
        """
        logger.debug(f"Scaling input by factor {alpha}")
        return abs(alpha) * self.evaluate(x)
    
    def triangle_inequality(self, x: T, y: T) -> bool:
        """
        Verify that the triangle inequality holds for the given inputs.
        
        Checks if p(x + y) <= p(x) + p(y).
        
        Parameters
        ----------
        x : T
            First input vector.
        y : T
            Second input vector.
            
        Returns
        -------
        bool
            True if the triangle inequality holds, False otherwise.
        """
        logger.debug("Checking triangle inequality")
        
        # Convert inputs to numpy arrays if they're not already
        if not isinstance(x, np.ndarray):
            x = np.array(x, dtype=float)
        if not isinstance(y, np.ndarray):
            y = np.array(y, dtype=float)
        
        # Ensure compatible dimensions
        if x.shape != y.shape:
            raise ValueError(f"Incompatible shapes: {x.shape} and {y.shape}")
        
        # Calculate the sum vector
        sum_vector = x + y
        
        # Evaluate the prenorm of each vector and the sum
        norm_x = self.evaluate(x)
        norm_y = self.evaluate(y)
        norm_sum = self.evaluate(sum_vector)
        
        # Check if the triangle inequality holds (with a small tolerance for floating-point errors)
        return norm_sum <= norm_x + norm_y + 1e-10
    
    def is_zero(self, x: T, tolerance: float = 1e-10) -> bool:
        """
        Check if the prenorm evaluates to zero (within a tolerance).
        
        Parameters
        ----------
        x : T
            The input vector to check.
        tolerance : float, optional
            The numerical tolerance for considering a value as zero.
            Default is 1e-10.
            
        Returns
        -------
        bool
            True if the prenorm of x is zero (within tolerance), False otherwise.
        """
        logger.debug(f"Checking if prenorm is zero with tolerance {tolerance}")
        return self.evaluate(x) < tolerance
    
    def is_definite(self) -> bool:
        """
        Check if this prenorm is actually a norm (i.e., it has the definiteness property).
        
        For LpPrenorm, this always returns False as it's designed to be a seminorm
        that might not distinguish all vectors.
        
        Returns
        -------
        bool
            Always False for LpPrenorm.
        """
        logger.debug("Checking if prenorm is definite")
        return False