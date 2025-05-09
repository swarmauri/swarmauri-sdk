from typing import TypeVar, Union, Tuple, Any
import logging
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.seminorms.ISeminorm import ISeminorm

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar("T", Union[str, callable, Tuple[float, ...], Sequence[float]])


@ComponentBase.register_type(SeminormBase, "PointEvaluationSeminorm")
class PointEvaluationSeminorm(SeminormBase):
    """
    Concrete implementation of SeminormBase that evaluates the function at a single point.

    This class provides the functionality to compute the seminorm by evaluating the input
    at a fixed point in its domain. The evaluation point is specified during initialization.

    Attributes:
        resource: str = ResourceTypes.SEMINORM.value
            The resource type identifier for this component.
        evaluation_point: Tuple[float, ...]
            The point at which to evaluate the function.
    """

    resource: str = ResourceTypes.SEMINORM.value
    evaluation_point: Tuple[float, ...]

    def __init__(self, evaluation_point: Tuple[float, ...] = (0.0,)) -> None:
        """
        Initializes the PointEvaluationSeminorm instance.

        Args:
            evaluation_point: Tuple[float, ...]
                The point at which to evaluate the function. Defaults to (0.0,).
        """
        super().__init__()
        if not isinstance(evaluation_point, tuple) or not all(
            isinstance(x, (int, float)) for x in evaluation_point
        ):
            raise ValueError("evaluation_point must be a tuple of numeric values")
        self_evaluation_point = evaluation_point

    def compute(self, input: T) -> float:
        """
        Computes the seminorm by evaluating the input at the specified point.

        Args:
            input: T
                The input to evaluate. This can be a callable, vector, or other evaluable type.

        Returns:
            float:
                The value of the input at the evaluation point.

        Raises:
            ValueError:
                If the input type is not supported or the evaluation point is invalid.
        """
        logger.debug(f"Computing seminorm at point {self_evaluation_point}")

        try:
            if callable(input):
                # If input is callable, evaluate it at the point
                return float(input(*self_evaluation_point))
            elif isinstance(input, (list, tuple)):
                # If input is a vector, take the value at the evaluation point index
                return float(input[self_evaluation_point[0]])
            else:
                # Handle other types if necessary
                raise TypeError(f"Unsupported input type: {type(input)}")
        except Exception as e:
            logger.error(f"Error during point evaluation: {str(e)}")
            raise ValueError(
                f"Failed to evaluate input at point {self_evaluation_point}"
            ) from e

    def check_triangle_inequality(self, a: T, b: T) -> bool:
        """
        Checks if the triangle inequality holds for the given inputs.

        Args:
            a: T
                The first input.
            b: T
                The second input.

        Returns:
            bool:
                True if seminorm(a + b) <= seminorm(a) + seminorm(b), False otherwise.
        """
        seminorm_a = self.compute(a)
        seminorm_b = self.compute(b)
        seminorm_a_plus_b = self.compute(a + b)
        return seminorm_a_plus_b <= seminorm_a + seminorm_b

    def check_scalar_homogeneity(self, a: T, scalar: float) -> bool:
        """
        Checks if scalar homogeneity holds for the given input and scalar.

        Args:
            a: T
                The input to check.
            scalar: float
                The scalar to check against.

        Returns:
            bool:
                True if seminorm(scalar * a) == scalar * seminorm(a), False otherwise.
        """
        scaled_input = scalar * a
        seminorm_scaled = self.compute(scaled_input)
        seminorm_a = self.compute(a)
        return seminorm_scaled == scalar * seminorm_a
