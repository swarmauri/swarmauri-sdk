from typing import TypeVar, Union, Sequence, Optional, Literal
import logging
import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.seminorms.ISeminorm import ISeminorm

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T', Union[Sequence[float], Sequence[Sequence[float]], str, callable])

@ComponentBase.register_model()
class LpSeminorm(SeminormBase):
    """
    A non-point-separating Lp seminorm implementation.

    This class provides a concrete implementation of the Lp seminorm that does not
    necessarily distinguish all vectors. It implements the core functionality for
    computing the seminorm, checking the triangle inequality, and verifying scalar
    homogeneity.

    Attributes:
        p: float
            The order of the Lp seminorm. Must satisfy p > 0.
        resource: str = ResourceTypes.SEMINORM.value
            The resource type identifier for this component.
        axis: Optional[int] = None
            The axis along which to compute the seminorm for array-like inputs.
            If None, the input is flattened before computation.
    """
    resource: str = ComponentBase.ResourceTypes.SEMINORM.value
    type: Literal["LpSeminorm"] = "LpSeminorm"

    def __init__(self, p: float, axis: Optional[int] = None):
        """
        Initialize the LpSeminorm instance.

        Args:
            p: float
                The order of the Lp seminorm. Must satisfy p > 0.
            axis: Optional[int] = None
                The axis along which to compute the seminorm for array-like inputs.
                If None, the input is flattened before computation.

        Raises:
            ValueError:
                If p is not greater than 0.
        """
        super().__init__()
        if p <= 0:
            raise ValueError("p must be greater than 0")
        self.p = p
        self.axis = axis

    def compute(self, input: T) -> float:
        """
        Compute the Lp seminorm of the given input.

        Args:
            input: T
                The input to compute the seminorm on. This can be a vector, matrix,
                string, or callable.

        Returns:
            float:
                The computed Lp seminorm value.

        Raises:
            ValueError:
                If the input cannot be processed.
        """
        logger.debug("Computing Lp seminorm for input of type %s", type(input))
        
        try:
            if isinstance(input, (str, callable)):
                # Handle string or callable input
                input = np.asarray(input)
            
            input_array = np.asarray(input)
            
            if input_array.ndim == 0:
                # Handle scalar input
                return 0.0
            
            if self.axis is not None:
                # Compute along specified axis
                return np.power(
                    np.sum(np.power(np.abs(input_array), self.p), axis=self.axis),
                    1.0 / self.p
                )
            else:
                # Flatten the array and compute
                flattened = input_array.ravel()
                return np.power(
                    np.sum(np.power(np.abs(flattened), self.p)),
                    1.0 / self.p
                )
            
        except Exception as e:
            logger.error("Failed to compute Lp seminorm: %s", str(e))
            raise ValueError(f"Failed to compute Lp seminorm: {str(e)}")
        
        return 0.0

    def check_triangle_inequality(self, a: T, b: T) -> bool:
        """
        Check if the triangle inequality holds for the given inputs.

        The triangle inequality states that for any two vectors a and b:
        seminorm(a + b) <= seminorm(a) + seminorm(b)

        Args:
            a: T
                The first input.
            b: T
                The second input.

        Returns:
            bool:
                True if the triangle inequality holds, False otherwise.
        """
        logger.debug("Checking triangle inequality for Lp seminorm")
        
        try:
            # Compute seminorms
            seminorm_a = self.compute(a)
            seminorm_b = self.compute(b)
            seminorm_ab = self.compute(a + b)
            
            # Check inequality
            return seminorm_ab <= seminorm_a + seminorm_b
            
        except Exception as e:
            logger.error("Failed to check triangle inequality: %s", str(e))
            return False

    def check_scalar_homogeneity(self, a: T, scalar: float) -> bool:
        """
        Check if scalar homogeneity holds for the given input and scalar.

        Scalar homogeneity states that for any vector a and scalar c >= 0:
        seminorm(c * a) = c * seminorm(a)

        Args:
            a: T
                The input to check.
            scalar: float
                The scalar to check against.

        Returns:
            bool:
                True if scalar homogeneity holds, False otherwise.
        """
        logger.debug("Checking scalar homogeneity for Lp seminorm")
        
        try:
            if scalar < 0:
                raise ValueError("Scalar must be non-negative")
                
            # Compute original seminorm
            seminorm_a = self.compute(a)
            
            # Compute scaled seminorm
            scaled_a = scalar * a
            seminorm_scaled = self.compute(scaled_a)
            
            # Compute expected value
            expected_seminorm = scalar ** (1.0 / self.p) * seminorm_a
            
            # Check if values are close (allowing for floating point errors)
            return np.isclose(seminorm_scaled, expected_seminorm)
            
        except Exception as e:
            logger.error("Failed to check scalar homogeneity: %s", str(e))
            return False