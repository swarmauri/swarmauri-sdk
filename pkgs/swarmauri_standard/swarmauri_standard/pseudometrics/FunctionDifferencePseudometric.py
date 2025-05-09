from typing import Union, Callable, List, Optional, Literal
import logging
from swarmauri_base.pseudometrics.PseudometricBase import PseudometricBase
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

logger = logging.getLogger(__name__)


@ComponentBase.register_type(PseudometricBase, "FunctionDifferencePseudometric")
class FunctionDifferencePseudometric(PseudometricBase):
    """
    A class providing function difference pseudometric functionality.

    This class implements the PseudometricBase interface to compute the distance
    between two functions based on their output differences at specified evaluation points.

    Attributes:
        f: First function to compare
        g: Second function to compare
        evaluation_points: List of points where functions are evaluated
        num_samples: Number of random samples to generate when evaluation_points is None
        resource: The resource type identifier for this component
    """

    type: Literal["FunctionDifferencePseudometric"] = "FunctionDifferencePseudometric"
    resource: Optional[str] = ResourceTypes.PSEUDOMETRIC.value

    def __init__(
        self,
        f: Callable = None,
        g: Callable = None,
        evaluation_points: List[float] = None,
        num_samples: int = 1000,
    ):
        """
        Initializes the FunctionDifferencePseudometric instance.

        Args:
            f: First function to compare
            g: Second function to compare
            evaluation_points: List of points where functions are evaluated
            num_samples: Number of random samples to generate when evaluation_points is None
        """
        super().__init__()
        self.f = f
        self.g = g
        self.evaluation_points = evaluation_points
        self.num_samples = num_samples
        logger.debug("Initialized FunctionDifferencePseudometric")

    def distance(
        self, x: Union[Callable, List[Callable]], y: Union[Callable, List[Callable]]
    ) -> float:
        """
        Computes the distance between two functions based on their output differences.

        Args:
            x: First function or list of functions
            y: Second function or list of functions

        Returns:
            float: Average absolute difference between function outputs at evaluation points

        Raises:
            ValueError: If functions are not callable or evaluation points are not specified
        """
        logger.debug("Computing function difference pseudometric")

        # Validate input
        if not self._is_callable(x) or not self._is_callable(y):
            raise ValueError("Inputs must be callable functions")

        # Ensure evaluation points are available
        if self.evaluation_points is None:
            # Generate random evaluation points in [0,1)
            import random

            self.evaluation_points = [random.random() for _ in range(self.num_samples)]

        total_diff = 0.0
        for point in self.evaluation_points:
            # Compute function outputs
            x_out = x(point)
            y_out = y(point)

            # Calculate absolute difference
            total_diff += abs(x_out - y_out)

        # Compute average difference
        return total_diff / len(self.evaluation_points)

    def check_symmetry(
        self, x: Union[Callable, List[Callable]], y: Union[Callable, List[Callable]]
    ) -> bool:
        """
        Verifies the symmetry property: d(x,y) = d(y,x).

        Args:
            x: First function
            y: Second function

        Returns:
            bool: True if symmetry holds, False otherwise
        """
        logger.debug("Checking symmetry for function difference pseudometric")
        return True

    def check_non_negativity(
        self, x: Union[Callable, List[Callable]], y: Union[Callable, List[Callable]]
    ) -> bool:
        """
        Verifies the non-negativity property: d(x,y) ≥ 0.

        Args:
            x: First function
            y: Second function

        Returns:
            bool: True if non-negativity holds, False otherwise
        """
        logger.debug("Checking non-negativity for function difference pseudometric")
        return True

    def check_triangle_inequality(
        self,
        x: Union[Callable, List[Callable]],
        y: Union[Callable, List[Callable]],
        z: Union[Callable, List[Callable]],
    ) -> bool:
        """
        Verifies the triangle inequality property: d(x,z) ≤ d(x,y) + d(y,z).

        Args:
            x: First function
            y: Second function
            z: Third function

        Returns:
            bool: True if triangle inequality holds, False otherwise
        """
        logger.debug(
            "Checking triangle inequality for function difference pseudometric"
        )
        return False  # Triangle inequality does not generally hold for function differences

    def check_weak_identity(
        self, x: Union[Callable, List[Callable]], y: Union[Callable, List[Callable]]
    ) -> bool:
        """
        Verifies the weak identity property: d(x,y) = 0 does not necessarily imply x = y.

        Args:
            x: First function
            y: Second function

        Returns:
            bool: True if weak identity holds (d(x,y)=0 does not imply x=y), False otherwise
        """
        logger.debug("Checking weak identity for function difference pseudometric")
        return True  # Functions can differ outside of evaluation points

    def _is_callable(self, input: Union[Callable, List[Callable]]) -> bool:
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
        Returns a string representation of the FunctionDifferencePseudometric instance.

        Returns:
            str: String representation
        """
        return f"FunctionDifferencePseudometric(f={self.f.__name__}, g={self.g.__name__}, evaluation_points={self.evaluation_points})"

    def __repr__(self) -> str:
        """
        Returns the official string representation of the FunctionDifferencePseudometric instance.

        Returns:
            str: Official string representation
        """
        return self.__str__()
