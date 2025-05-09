import logging
from typing import Union, Any, Callable, Sequence
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.norms.NormBase import NormBase
import numpy as np

logger = logging.getLogger(__name__)

@ComponentBase.register_type(NormBase, "SupremumComplexNorm")
class SupremumComplexNorm(NormBase):
    """
    A class to compute the supremum norm for complex-valued functions.

    The supremum norm is defined as the maximum absolute value of a function
    over a specified interval [a, b]. This class provides the functionality
    to compute this norm for various input types, including callable functions
    and sequences.

    Attributes:
        a (float): The start of the interval.
        b (float): The end of the interval.
        num_points (int): Number of points to sample in the interval for evaluation.
    """

    def __init__(self, a: float = 0.0, b: float = 1.0, num_points: int = 1000):
        """
        Initializes the SupremumComplexNorm with the specified interval.

        Args:
            a (float): Start of the interval. Defaults to 0.0.
            b (float): End of the interval. Defaults to 1.0.
            num_points (int): Number of points to sample in the interval. Defaults to 1000.
        """
        super().__init__()
        self.a = a
        self.b = b
        self.num_points = num_points
        logger.debug(f"Initialized SupremumComplexNorm with interval [{a}, {b}]")

    def compute(self, x: Union[Callable, Sequence, Any]) -> float:
        """
        Computes the supremum norm of the input.

        The input can be a callable function or a sequence. For callables,
        the function is evaluated at multiple points in the interval [a, b],
        and the maximum absolute value is returned. For sequences, the maximum
        absolute value of the elements is returned.

        Args:
            x: The input to compute the norm for. Can be a callable function,
                a sequence of values, or other compatible types.

        Returns:
            float: The computed supremum norm value.

        Raises:
            ValueError: If the input type is not supported.
            Exception: If any error occurs during function evaluation.
        """
        logger.debug(f"Computing supremum norm for input: {x}")
        
        try:
            if callable(x):
                # Generate points in the interval
                t = np.linspace(self.a, self.b, self.num_points)
                # Evaluate the function at these points
                values = x(t)
                # Compute absolute values
                abs_values = np.abs(values)
                # Find the maximum
                norm = np.max(abs_values)
            elif isinstance(x, Sequence):
                # Compute absolute values of the sequence
                abs_values = [abs(val) for val in x]
                # Find the maximum
                norm = max(abs_values)
            else:
                raise ValueError(f"Unsupported input type: {type(x)}")
        except Exception as e:
            logger.error(f"Error during norm computation: {str(e)}")
            raise

        logger.debug(f"Computed supremum norm: {norm}")
        return norm

    def __str__(self) -> str:
        """
        Returns a string representation of the norm.
        """
        return f"SupremumComplexNorm(a={self.a}, b={self.b}, num_points={self.num_points})"

    def __repr__(self) -> str:
        """
        Returns a string representation of the norm that can be used to recreate the object.
        """
        return f"SupremumComplexNorm(a={self.a}, b={self.b}, num_points={self.num_points})"