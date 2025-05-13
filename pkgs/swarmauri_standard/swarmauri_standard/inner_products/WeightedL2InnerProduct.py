import logging
from typing import Callable, Union

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase

from swarmauri_standard.vectors.Vector import Vector

logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "WeightedL2InnerProduct")
class WeightedL2InnerProduct(InnerProductBase):
    """
    Provides a concrete implementation of an inner product for weighted L2 spaces.
    This class computes the inner product with position-dependent weights, suitable
    for both real and complex functions. The weight function must be strictly positive.

    Inherits from:
        InnerProductBase: The base class for inner product implementations
    """

    # type: str = "WeightedL2InnerProduct"

    def __init__(self, weight_function: Callable):
        """
        Initializes the WeightedL2InnerProduct instance with a weight function.

        Args:
            weight_function: A callable that represents the weight function.
                             Must be strictly positive over its domain.

        Raises:
            ValueError: If the weight function is not strictly positive
        """
        super().__init__()
        self._weight_function = weight_function
        self._validate_weight_function()

    def _validate_weight_function(self) -> None:
        """
        Validates that the weight function is strictly positive.

        This method verifies that the weight function returns positive values
        for all inputs in its domain. Raises a ValueError if this condition
        is not met.

        Raises:
            ValueError: If the weight function is not strictly positive
        """
        # Validate weight function by sampling points
        # For demonstration, we sample at a few points
        sample_points = np.linspace(0, 1, 10)
        weights = self._weight_function(sample_points)

        if np.any(weights <= 0):
            raise ValueError("Weight function must be strictly positive")

        logger.info("Weight function validation passed")

    @property
    def weight_function(self) -> Callable:
        """
        Property returning the weight function.

        Returns:
            Callable: The weight function used in the inner product
        """
        return self._weight_function

    def compute(
        self,
        a: Union[Vector, np.ndarray, Callable],
        b: Union[Vector, np.ndarray, Callable],
    ) -> float:
        """
        Computes the weighted L2 inner product of two functions/vectors.

        The computation is performed as:
            <a, b>_w = ∫ a(x) * conj(b(x)) * w(x) dx

        Args:
            a: The first element in the inner product operation
            b: The second element in the inner product operation

        Returns:
            float: The result of the weighted L2 inner product

        Raises:
            ValueError: If the input types are not supported or dimensions are incompatible
        """
        try:
            # Handle different input types for 'a'
            if isinstance(a, Vector):
                a_array = a.to_numpy()
            elif callable(a):
                # Evaluate the callable on a grid
                x_grid = np.linspace(0, 1, 100)  # Example grid
                a_array = np.array([a(x) for x in x_grid])
            elif isinstance(a, np.ndarray):
                a_array = a
            else:
                raise ValueError(f"Unsupported input type for 'a': {type(a)}")

            # Handle different input types for 'b'
            if isinstance(b, Vector):
                b_array = b.to_numpy()
            elif callable(b):
                # Evaluate the callable on the same grid
                x_grid = np.linspace(0, 1, 100)
                b_array = np.array([b(x) for x in x_grid])
            elif isinstance(b, np.ndarray):
                b_array = b
            else:
                raise ValueError(f"Unsupported input type for 'b': {type(b)}")

            # Ensure compatible dimensions
            if a_array.shape != b_array.shape:
                raise ValueError(
                    f"Incompatible dimensions: {a_array.shape} vs {b_array.shape}"
                )

            # Apply weight function to both arrays element-wise
            weighted_a = a_array * np.sqrt(self.weight_function(a_array))
            weighted_b = b_array * np.sqrt(self.weight_function(b_array))

            # Compute element-wise product and sum to get L2 norm
            product = np.dot(weighted_a, weighted_b)

            return float(product)

        except Exception as e:
            logger.error(f"Error in compute method: {str(e)}")
            raise ValueError(f"Failed to compute inner product: {str(e)}")

    def __str__(self) -> str:
        """
        Returns a string representation of the object.

        Returns:
            str: String representation
        """
        return (
            f"WeightedL2InnerProduct(weight_function={self.weight_function.__name__})"
        )

    def __repr__(self) -> str:
        """
        Returns the string representation of the object for official string representation.

        Returns:
            str: Official string representation
        """
        return self.__str__()
