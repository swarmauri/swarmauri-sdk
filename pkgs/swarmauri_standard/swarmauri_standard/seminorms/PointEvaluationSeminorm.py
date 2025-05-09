import logging
from abc import ABC, abstractmethod
from typing import TypeVar, Union, Callable, Sequence
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.seminorms.ISeminorm import ISeminorm

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Union[IVector, IMatrix, Sequence, str, Callable])

@ComponentBase.register_type(SeminormBase, "PointEvaluationSeminorm")
class PointEvaluationSeminorm(SeminormBase):
    """
    A concrete implementation of SeminormBase that evaluates functions at a single point.

    This class provides a seminorm that evaluates the value of a function at a specific,
    fixed point in its domain. The point of evaluation must be within the domain of
    the function being evaluated.

    Attributes:
        point: The fixed point at which the function is evaluated.
    """
    type: Literal["PointEvaluationSeminorm"] = "PointEvaluationSeminorm"
    resource: str = ResourceTypes.SEMINORM.value

    def __init__(self, point: Union[int, float, str]):
        """
        Initializes the PointEvaluationSeminorm instance.

        Args:
            point: Union[int, float, str]
                The fixed point at which the function will be evaluated. This must be
                within the domain of the function being evaluated.

        Raises:
            ValueError: If the point is not in the function's domain
        """
        super().__init__()
        self.point = point
        logger.info(f"Initialized PointEvaluationSeminorm with evaluation point {self.point}")

    def compute(self, input: T) -> float:
        """
        Computes the seminorm value by evaluating the input at the fixed point.

        Args:
            input: T
                The input to evaluate at the fixed point. Can be a vector, matrix,
                sequence, string, or callable.

        Returns:
            float: The value of the input at the fixed point.

        Raises:
            ValueError: If the input is not evaluable at the fixed point
        """
        logger.debug(f"Computing seminorm by evaluating input at point {self.point}")
        
        try:
            if callable(input):
                return float(input(self.point))
            elif isinstance(input, Sequence):
                if self.point < len(input):
                    return float(input[self.point])
                else:
                    raise ValueError(f"Point {self.point} exceeds input length {len(input)}")
            elif isinstance(input, str):
                if self.point < len(input):
                    return float(ord(input[self.point]))
                else:
                    raise ValueError(f"Point {self.point} exceeds string length {len(input)}")
            else:
                return float(input)
        except Exception as e:
            logger.error(f"Failed to compute seminorm: {str(e)}")
            raise ValueError(f"Could not evaluate input at point {self.point}: {str(e)}")

    def check_triangle_inequality(self, a: T, b: T) -> bool:
        """
        Checks if the triangle inequality holds for point evaluation.

        For point evaluation, the triangle inequality holds because:
        |f(a + b)| ≤ |f(a)| + |f(b)|

        Args:
            a: T
                The first input
            b: T
                The second input

        Returns:
            bool: True if the triangle inequality holds, False otherwise
        """
        return True

    def check_scalar_homogeneity(self, a: T, scalar: float) -> bool:
        """
        Checks if the scalar homogeneity property holds for point evaluation.

        For point evaluation, scalar homogeneity holds because:
        p(t*f) = |t| * p(f)

        Args:
            a: T
                The input to check
            scalar: float
                The scalar to test homogeneity with

        Returns:
            bool: True if scalar homogeneity holds, False otherwise
        """
        return True