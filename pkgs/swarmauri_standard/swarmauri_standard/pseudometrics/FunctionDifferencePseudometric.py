from typing import Union, List, Tuple, Callable, Optional, Literal
from abc import ABC
import numpy as np
import logging

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.pseudometrics import PseudometricBase
from core.swarmauri_core.pseudometrics.IPseudometric import IPseudometric

logger = logging.getLogger(__name__)


@ComponentBase.register_type(PseudometricBase, "FunctionDifferencePseudometric")
class FunctionDifferencePseudometric(PseudometricBase):
    """
    A concrete implementation of PseudometricBase for measuring the difference between functions.

    This class measures the output difference between two functions based on their value differences
    on a specific set of points. The functions must be defined on the same domain, and the class
    provides functionality to handle both provided evaluation points and random sampling.

    Implements:
    - distance()
    - distances()
    - check_non_negativity()
    - check_symmetry()
    - check_triangle_inequality()
    - check_weak_identity()
    """
    type: Literal["FunctionDifferencePseudometric"] = "FunctionDifferencePseudometric"
    
    def __init__(
        self,
        points: Optional[Union[List[float], Tuple[float]]] = None,
        num_sample_points: int = 1000,
        random_seed: Optional[int] = None
    ):
        """
        Initialize the FunctionDifferencePseudometric instance.

        Args:
            points: Optional list or tuple of points to evaluate the functions at.
                   If not provided, random points will be generated.
            num_sample_points: Number of random points to generate if points is None.
            random_seed: Seed for random number generation. Ensures reproducibility.
        """
        super().__init__()
        self.points = points if points is not None else self._generate_sample_points(
            num_sample_points,
            random_seed
        )
        self.num_sample_points = num_sample_points
        self.random_seed = random_seed
        logger.debug("Initialized FunctionDifferencePseudometric with %d points",
                   len(self.points))

    def _generate_sample_points(
        self,
        num_points: int,
        random_seed: Optional[int]
    ) -> np.ndarray:
        """
        Generate random sample points for function evaluation.

        Args:
            num_points: Number of points to generate.
            random_seed: Seed for random number generation.

        Returns:
            np.ndarray: Array of random points in the range [-1, 1].
        """
        np.random.seed(random_seed)
        return np.random.uniform(low=-1.0, high=1.0, size=num_points)

    def distance(self, x: Callable, y: Callable) -> float:
        """
        Calculate the distance between two functions based on their value differences.

        Args:
            x: The first function.
            y: The second function.

        Returns:
            float: The average absolute difference between the function outputs at the specified points.

        Raises:
            ValueError: If the functions are not callable or not defined on the same domain.
        """
        logger.debug("Computing function distance")
        
        if not callable(x) or not callable(y):
            raise ValueError("Both inputs must be callable functions")
            
        differences = [abs(x(point) - y(point)) for point in self.points]
        return float(np.mean(differences))

    def distances(self, x: Callable, y_list: Union[List[Callable], Tuple[Callable]]) -> List[float]:
        """
        Calculate distances from a reference function to a list of functions.

        Args:
            x: The reference function.
            y_list: List or tuple of functions to measure distances to.

        Returns:
            List[float]: List of distances from x to each function in y_list.
        """
        logger.debug("Computing distances to multiple functions")
        return [self.distance(x, y) for y in y_list]

    def check_non_negativity(self, x: Callable, y: Callable) -> bool:
        """
        Check if the distance satisfies non-negativity: d(x,y) ≥ 0.

        Args:
            x: The first function.
            y: The second function.

        Returns:
            bool: True if the distance is non-negative, False otherwise.
        """
        return self.distance(x, y) >= 0.0

    def check_symmetry(self, x: Callable, y: Callable) -> bool:
        """
        Check if the distance satisfies symmetry: d(x,y) = d(y,x).

        Args:
            x: The first function.
            y: The second function.

        Returns:
            bool: True if the distance is symmetric, False otherwise.
        """
        return self.distance(x, y) == self.distance(y, x)

    def check_triangle_inequality(self, x: Callable, y: Callable, z: Callable) -> bool:
        """
        Check if the distance satisfies triangle inequality: d(x,z) ≤ d(x,y) + d(y,z).

        Args:
            x: The first function.
            y: The second function.
            z: The third function.

        Returns:
            bool: True if triangle inequality holds.
        """
        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)
        return d_xz <= d_xy + d_yz

    def check_weak_identity(self, x: Callable, y: Callable) -> bool:
        """
        Check if the distance satisfies weak identity of indiscernibles:
        d(x,y) = 0 if and only if x and y are not distinguishable.

        Args:
            x: The first function.
            y: The second function.

        Returns:
            bool: True if weak identity holds, False otherwise.
        """
        return self.distance(x, y) == 0.0