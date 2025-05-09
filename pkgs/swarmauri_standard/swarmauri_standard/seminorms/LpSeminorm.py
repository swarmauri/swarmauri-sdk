import logging
import numpy as np
from typing import TypeVar, Union, Sequence, Callable
from abc import abstractmethod
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.seminorms.ISeminorm import ISeminorm

logger = logging.getLogger(__name__)

T = TypeVar('T', Sequence, Union[Sequence, Callable], str, Callable)

@ComponentBase.register_type(SeminormBase, "LpSeminorm")
class LpSeminorm(SeminormBase):
    """
    A concrete implementation of a non-point-separating Lp seminorm.

    This class provides the implementation for computing the Lp seminorm,
    which is a non-point-separating variant of the standard Lp norm.
    The seminorm is defined as the sum of the absolute values of the input
    elements raised to the power of p, then taking the p-th root of the sum.

    Inherits From:
        SeminormBase: The base class for all seminorm implementations.

    Attributes:
        p: float
            The parameter of the Lp seminorm, must be in (0, ∞).
    """
    resource: str = ResourceTypes.SEMINORM.value
    """
    The resource type identifier for seminorm components.
    """
    
    def __init__(self, p: float):
        """
        Initializes the LpSeminorm instance with the given parameter p.

        Args:
            p: float
                The parameter for the Lp seminorm. Must be in (0, ∞).

        Raises:
            ValueError: If p is not in (0, ∞).
        """
        super().__init__()
        if p <= 0:
            logger.error("Invalid value for p. p must be in (0, ∞).")
            raise ValueError("p must be in (0, ∞)")
        self.p: float = p

    def compute(self, input: T) -> float:
        """
        Computes the Lp seminorm value for the given input.

        Args:
            input: T
                The input to compute the seminorm for. Can be a vector, matrix,
                sequence, string, or callable. For this implementation, the input
                should be a sequence of numbers.

        Returns:
            float: The computed seminorm value.

        Raises:
            NotImplementedError: If the input type is not supported.
        """
        logger.info("Computing Lp seminorm for input of type %s", type(input).__name__)
        
        try:
            # Convert input to numpy array for easier manipulation
            arr = np.asarray(input)
            
            # Compute absolute values of elements
            abs_values = np.abs(arr)
            
            # Raise to the power of p
            powered = np.power(abs_values, self.p)
            
            # Sum the powered values
            sum_powered = np.sum(powered)
            
            # Take the p-th root
            result = np.power(sum_powered, 1.0 / self.p)
            
            logger.info("Computed Lp seminorm: %s", result)
            return result
            
        except Exception as e:
            logger.error("Error computing Lp seminorm: %s", str(e))
            raise NotImplementedError(f"Input type {type(input).__name__} is not supported")
            
    def check_triangle_inequality(self, a: T, b: T) -> bool:
        """
        Checks if the triangle inequality holds for the given inputs.

        Args:
            a: T
                The first input vector
            b: T
                The second input vector

        Returns:
            bool: True if ||a + b||_p <= ||a||_p + ||b||_p, False otherwise
        """
        logger.info("Checking triangle inequality for Lp seminorm")
        
        try:
            # Compute seminorms
            norm_a = self.compute(a)
            norm_b = self.compute(b)
            norm_ab = self.compute([a, b])
            
            # Check inequality
            return norm_ab <= (norm_a + norm_b)
            
        except Exception as e:
            logger.error("Error checking triangle inequality: %s", str(e))
            return False
            
    def check_scalar_homogeneity(self, a: T, scalar: float) -> bool:
        """
        Checks if the scalar homogeneity property holds for the given input and scalar.

        Args:
            a: T
                The input vector to check
            scalar: float
                The scalar to test homogeneity with

        Returns:
            bool: True if ||scalar * a||_p = |scalar| * ||a||_p, False otherwise
        """
        logger.info("Checking scalar homogeneity for Lp seminorm")
        
        try:
            # Compute original norm
            norm_a = self.compute(a)
            
            # Compute norm after scaling
            scaled_a = [x * scalar for x in a]
            norm_scaled = self.compute(scaled_a)
            
            # Compare with |scalar| * norm_a
            expected = abs(scalar) * norm_a
            return np.isclose(norm_scaled, expected)
            
        except Exception as e:
            logger.error("Error checking scalar homogeneity: %s", str(e))
            return False