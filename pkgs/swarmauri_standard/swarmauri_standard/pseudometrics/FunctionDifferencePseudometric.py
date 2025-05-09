from typing import TypeVar, Iterable, Optional, Union, Tuple, Callable
import numpy as np
import logging
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.pseudometrics.IPseudometric import IPseudometric

# Configure logging
logger = logging.getLogger(__name__)

# Define type variables for input types
InputTypes = TypeVar('InputTypes', Callable, Iterable[float])

@ComponentBase.register_type(PseudometricBase, "FunctionDifferencePseudometric")
class FunctionDifferencePseudometric(PseudometricBase):
    """
    Concrete implementation of PseudometricBase for measuring output difference of functions.

    This class provides a pseudometric that measures the difference between two functions based on their
    output values at specified evaluation points. The distance is computed as the average absolute difference
    between the function outputs at these points.

    Attributes:
        resource: str = ResourceTypes.PSEUDOMETRIC.value
            The resource type identifier for this component.
        evaluation_points: Optional[Iterable[float]]
            Specific points in the domain where the functions will be evaluated.
            If not provided, default points will be generated.
        sample_count: int
            Number of points to sample from the domain when evaluation_points is not provided.
    """

    resource: str = Field(default=ResourceTypes.PSEUDOMETRIC.value)
    evaluation_points: Optional[Iterable[float]] = None
    sample_count: int = 10

    def __init__(self, evaluation_points: Optional[Iterable[float]] = None, sample_count: int = 10) -> None:
        """
        Initializes the FunctionDifferencePseudometric instance.

        Args:
            evaluation_points: Optional[Iterable[float]]
                Specific points in the domain where the functions will be evaluated.
                If not provided, default points will be generated using sample_count.
            sample_count: int
                Number of points to sample from the domain when evaluation_points is not provided.
                Defaults to 10.
        """
        super().__init__()
        self.evaluation_points = evaluation_points
        self.sample_count = sample_count

        # Generate default evaluation points if not provided
        if evaluation_points is None:
            self._generate_default_evaluation_points()

    def _generate_default_evaluation_points(self) -> None:
        """
        Generates default evaluation points using numpy.linspace.
        The domain is assumed to be [0, 1].
        """
        domain_start = 0.0
        domain_end = 1.0
        self.evaluation_points = np.linspace(domain_start, domain_end, self.sample_count)

    def distance(self, x: Callable, y: Callable) -> float:
        """
        Compute the distance between two functions based on their output differences at specified points.

        Args:
            x: Callable
                The first function to evaluate.
            y: Callable
                The second function to evaluate.

        Returns:
            float:
                The average absolute difference between the function outputs at the evaluation points.

        Raises:
            ValueError:
                If evaluation points are not specified and cannot be generated.
            TypeError:
                If either x or y is not callable.
        """
        if not callable(x) or not callable(y):
            raise TypeError("Both inputs must be callable functions")

        if self.evaluation_points is None:
            raise ValueError("Evaluation points must be specified or generated")

        total = 0.0
        for point in self.evaluation_points:
            # Evaluate both functions at the current point
            fx = x(point)
            fy = y(point)
            # Compute absolute difference and add to total
            total += abs(fx - fy)

        # Compute average difference
        average_difference = total / len(self.evaluation_points)
        logger.debug(f"Computed distance: {average_difference}")
        return average_difference

    def distances(self, x: Callable, ys: Iterable[Callable]) -> Iterable[float]:
        """
        Compute distances from function x to multiple functions ys.

        Args:
            x: Callable
                The reference function.
            ys: Iterable[Callable]
                Collection of functions to compute distances to.

        Returns:
            Iterable[float]:
                An iterable of distances from x to each function in ys.

        Raises:
            TypeError:
                If x is not callable or any function in ys is not callable.
        """
        if not callable(x):
            raise TypeError("x must be a callable function")

        distances = []
        for y in ys:
            if not callable(y):
                raise TypeError(f"Function {y} is not callable")
            distances.append(self.distance(x, y))
            
        return distances

    def check_non_negativity(self, x: Callable, y: Callable) -> bool:
        """
        Check if the distance satisfies non-negativity.

        Args:
            x: Callable
                The first function.
            y: Callable
                The second function.

        Returns:
            bool:
                True if distance(x, y) >= 0, False otherwise.
        """
        distance = self.distance(x, y)
        return distance >= 0

    def check_symmetry(self, x: Callable, y: Callable) -> bool:
        """
        Check if the distance satisfies symmetry.

        Args:
            x: Callable
                The first function.
            y: Callable
                The second function.

        Returns:
            bool:
                True if distance(x, y) == distance(y, x), False otherwise.
        """
        return self.distance(x, y) == self.distance(y, x)

    def check_triangle_inequality(self, x: Callable, y: Callable, z: Callable) -> bool:
        """
        Check if the distance satisfies the triangle inequality.

        Args:
            x: Callable
                The first function.
            y: Callable
                The second function.
            z: Callable
                The third function.

        Returns:
            bool:
                True if distance(x, z) <= distance(x, y) + distance(y, z), False otherwise.
        """
        return self.distance(x, z) <= self.distance(x, y) + self.distance(y, z)

    def check_weak_identity(self, x: Callable, y: Callable) -> bool:
        """
        Check if the distance satisfies weak identity of indiscernibles.

        Args:
            x: Callable
                The first function.
            y: Callable
                The second function.

        Returns:
            bool:
                True if x == y implies distance(x, y) == 0, False otherwise.
        """
        return self.distance(x, y) == 0