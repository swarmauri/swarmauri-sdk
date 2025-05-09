from typing import Union, List, Literal, Sequence, Optional
from pydantic import Field
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_standard.norms.GeneralLpNorm import GeneralLpNorm
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class LpMetric(MetricBase):
    """
    Implementation of the Lp metric for vector spaces.

    This class provides a concrete implementation of the MetricBase class for
    computing distances using the Lp norm. The Lp norm is parameterized by p,
    where p must be greater than 1.

    Inherits From:
        MetricBase: Base class for all metric implementations

    Attributes:
        p (float): The parameter for the Lp norm, must be > 1 and finite
        type (Literal["LpMetric"]): Type identifier for the component
    """

    type: Literal["LpMetric"] = "LpMetric"
    p: float = Field(default=2.0)

    def __init__(self, p: float = 2.0):
        """
        Initialize the LpMetric instance.

        Args:
            p (float): The parameter for the Lp norm, must be > 1 and finite

        Raises:
            ValueError: If p is not greater than 1 or is not finite
        """
        if not (isinstance(p, (float, int)) and p > 1 and p != float("inf")):
            raise ValueError("p must be a finite float greater than 1")

        self.p = p
        super().__init__()

    def distance(
        self, x: Union[Sequence, Callable, str], y: Union[Sequence, Callable, str]
    ) -> float:
        """
        Compute the Lp distance between two points.

        The Lp distance is defined as:

        For vectors x and y:
        distance(x, y) = ||x - y||_p

        For matrices X and Y:
        distance(X, Y) = max(||X[i] - Y[i]||_p for all rows i)

        Args:
            x: The first point. Can be a vector, matrix, string, or callable.
            y: The second point. Can be a vector, matrix, string, or callable.

        Returns:
            float: The computed Lp distance between x and y.

        Raises:
            ValueError: If the input types are not supported
        """
        try:
            # Convert callables or strings to their representation
            if callable(x):
                x = x()
            if callable(y):
                y = y()

            # Handle string representations
            if isinstance(x, str):
                x = eval(x)
            if isinstance(y, str):
                y = eval(y)

            # Compute the difference
            diff = [xi - yi for xi, yi in zip(x, y)]

            # Compute the Lp norm of the difference
            norm = GeneralLpNorm(self.p)
            distance = norm.compute(diff)

            return distance

        except Exception as e:
            logger.error(f"Failed to compute Lp distance: {str(e)}")
            raise ValueError(f"Failed to compute Lp distance: {str(e)}")

    def distances(
        self,
        x: Union[Sequence, Callable, str],
        ys: List[Union[Sequence, Callable, str]],
    ) -> List[float]:
        """
        Compute distances from a single point to multiple points.

        Args:
            x: The reference point. Can be a vector, matrix, string, or callable.
            ys: List of points to compute distances to. Each can be a vector,
                matrix, string, or callable.

        Returns:
            List[float]: List of distances from x to each point in ys.

        Raises:
            ValueError: If any input type is not supported
        """
        try:
            distances = []
            for y in ys:
                distances.append(self.distance(x, y))
            return distances
        except Exception as e:
            logger.error(f"Failed to compute distances: {str(e)}")
            raise ValueError(f"Failed to compute distances: {str(e)}")

    def check_non_negativity(
        self, x: Union[Sequence, Callable, str], y: Union[Sequence, Callable, str]
    ) -> Literal[True]:
        """
        Verify the non-negativity property: d(x, y) ≥ 0.

        Args:
            x: The first point. Can be a vector, matrix, string, or callable.
            y: The second point. Can be a vector, matrix, string, or callable.

        Returns:
            Literal[True]: True if the non-negativity property holds.

        Raises:
            AssertionError: If the non-negativity property is violated
        """
        distance = self.distance(x, y)
        if distance < 0:
            logger.error("Non-negativity violation: Negative distance found")
            raise AssertionError("Non-negativity violation: Negative distance found")
        return True

    def check_identity(
        self, x: Union[Sequence, Callable, str], y: Union[Sequence, Callable, str]
    ) -> Literal[True]:
        """
        Verify the identity of indiscernibles property: d(x, y) = 0 if and only if x = y.

        Args:
            x: The first point. Can be a vector, matrix, string, or callable.
            y: The second point. Can be a vector, matrix, string, or callable.

        Returns:
            Literal[True]: True if the identity property holds.

        Raises:
            AssertionError: If the identity property is violated
        """
        distance = self.distance(x, y)
        if distance == 0:
            try:
                if x != y:
                    logger.error(
                        "Identity violation: Different points have zero distance"
                    )
                    raise AssertionError(
                        "Identity violation: Different points have zero distance"
                    )
            except Exception as e:
                raise AssertionError(
                    "Identity violation: Different points have zero distance"
                ) from e
        else:
            if x == y:
                logger.error(
                    "Identity violation: Identical points have non-zero distance"
                )
                raise AssertionError(
                    "Identity violation: Identical points have non-zero distance"
                )
        return True

    def check_symmetry(
        self, x: Union[Sequence, Callable, str], y: Union[Sequence, Callable, str]
    ) -> Literal[True]:
        """
        Verify the symmetry property: d(x, y) = d(y, x).

        Args:
            x: The first point. Can be a vector, matrix, string, or callable.
            y: The second point. Can be a vector, matrix, string, or callable.

        Returns:
            Literal[True]: True if the symmetry property holds.

        Raises:
            AssertionError: If the symmetry property is violated
        """
        distance_xy = self.distance(x, y)
        distance_yx = self.distance(y, x)

        if not (distance_xy == distance_yx):
            logger.error("Symmetry violation: d(x, y) != d(y, x)")
            raise AssertionError("Symmetry violation: d(x, y) != d(y, x)")
        return True

    def check_triangle_inequality(
        self,
        x: Union[Sequence, Callable, str],
        y: Union[Sequence, Callable, str],
        z: Union[Sequence, Callable, str],
    ) -> Literal[True]:
        """
        Verify the triangle inequality property: d(x, z) ≤ d(x, y) + d(y, z).

        Args:
            x: The first point. Can be a vector, matrix, string, or callable.
            y: The second point. Can be a vector, matrix, string, or callable.
            z: The third point. Can be a vector, matrix, string, or callable.

        Returns:
            Literal[True]: True if the triangle inequality property holds.

        Raises:
            AssertionError: If the triangle inequality is violated
        """
        distance_xz = self.distance(x, z)
        distance_xy = self.distance(x, y)
        distance_yz = self.distance(y, z)

        if distance_xz > distance_xy + distance_yz:
            logger.error("Triangle inequality violation")
            raise AssertionError("Triangle inequality violation")
        return True
