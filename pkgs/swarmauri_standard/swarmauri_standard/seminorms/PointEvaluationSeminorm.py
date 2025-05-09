from typing import Union, Callable, Optional, Literal
import logging
from swarmauri_base.seminorms.SeminormBase import SeminormBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SeminormBase, "PointEvaluationSeminorm")
class PointEvaluationSeminorm(SeminormBase):
    """
    A class providing point evaluation seminorm functionality.

    This class implements the SeminormBase interface to evaluate functions at a single fixed point.
    It provides the capability to compute the seminorm by evaluating the function at a specified point
    in the domain.

    Attributes:
        fixed_point: The point at which the function is evaluated
        resource: The resource type identifier for this component
    """

    def __init__(self, fixed_point: Union[int, float, tuple, list] = None):
        """
        Initializes the PointEvaluationSeminorm instance.

        Args:
            fixed_point: The fixed point where the function will be evaluated
        """
        super().__init__()
        self.fixed_point = fixed_point
        self.resource = ResourceTypes.SEMINORM.value
        logger.debug("Initialized PointEvaluationSeminorm")

    def compute(
        self, input: Union[IVector, IMatrix, str, Callable, list, tuple]
    ) -> float:
        """
        Computes the seminorm value by evaluating the input at the fixed point.

        Args:
            input: The input to compute the seminorm for. Supported types are:
                - IVector: High-dimensional vector
                - IMatrix: Matrix structure
                - str: String input
                - Callable: Callable function
                - list: List of elements
                - tuple: Tuple of elements

        Returns:
            float: The computed seminorm value

        Raises:
            TypeError: If input type is not supported
            ValueError: If fixed_point is not set
        """
        if self.fixed_point is None:
            raise ValueError("Fixed point must be set before computation")

        logger.debug(f"Computing seminorm at fixed point {self.fixed_point}")

        if self._is_callable(input):
            result = input(self.fixed_point)
        elif self._is_vector(input) or self._is_sequence(input):
            if isinstance(input, IVector):
                result = input[self.fixed_point]
            else:
                result = input[self.fixed_point]
        else:
            raise TypeError(f"Unsupported input type: {type(input).__name__}")

        return float(result)

    def check_triangle_inequality(
        self,
        a: Union[IVector, IMatrix, str, Callable, list, tuple],
        b: Union[IVector, IMatrix, str, Callable, list, tuple],
    ) -> bool:
        """
        Verifies the triangle inequality property: |a + b| <= |a| + |b| at the fixed point.

        Args:
            a: First element to check
            b: Second element to check

        Returns:
            bool: True if triangle inequality holds, False otherwise
        """
        logger.debug(f"Checking triangle inequality at fixed point {self.fixed_point}")

        a_value = self.compute(a)
        b_value = self.compute(b)
        sum_value = self.compute(a + b)

        triangle_inequality_holds = abs(sum_value) <= abs(a_value) + abs(b_value)
        logger.debug(f"Triangle inequality holds: {triangle_inequality_holds}")
        return triangle_inequality_holds

    def check_scalar_homogeneity(
        self,
        a: Union[IVector, IMatrix, str, Callable, list, tuple],
        scalar: Union[int, float],
    ) -> bool:
        """
        Verifies the scalar homogeneity property: |s * a| = |s| * |a| at the fixed point.

        Args:
            a: Element to check
            scalar: Scalar value to scale with

        Returns:
            bool: True if scalar homogeneity holds, False otherwise
        """
        logger.debug(f"Checking scalar homogeneity at fixed point {self.fixed_point}")

        scaled_a = scalar * a
        computed_scaled = self.compute(scaled_a)
        computed_a = self.compute(a)
        scalar_abs = abs(scalar)

        scalar_homogeneity_holds = abs(computed_scaled) == scalar_abs * abs(computed_a)
        logger.debug(f"Scalar homogeneity holds: {scalar_homogeneity_holds}")
        return scalar_homogeneity_holds

    def _is_callable(
        self, input: Union[IVector, IMatrix, str, Callable, list, tuple]
    ) -> bool:
        """
        Helper method to check if input is a callable function.

        Args:
            input: Input to check

        Returns:
            bool: True if input is callable, False otherwise
        """
        return isinstance(input, Callable)

    def __str__(self) -> str:
        """
        Returns a string representation of the PointEvaluationSeminorm instance.

        Returns:
            str: String representation
        """
        return f"PointEvaluationSeminorm(fixed_point={self.fixed_point})"

    def __repr__(self) -> str:
        """
        Returns the official string representation of the PointEvaluationSeminorm instance.

        Returns:
            str: Official string representation
        """
        return self.__str__()
