from typing import Literal, Union, List, Callable
import logging
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.metrics.IMetric import MetricViolationError
from swarmauri_standard.norms.SobolevNorm import SobolevNorm

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "SobolevMetric")
class SobolevMetric(MetricBase):
    """
    A class implementing the Sobolev metric, which measures the distance between functions
    by considering both their values and derivatives up to a specified order.

    The Sobolev metric combines the L2 norms of a function and its derivatives, providing
    a comprehensive measure of both the function's value and its smoothness.

    Attributes:
        order: The highest order of derivatives to include in the metric computation.
            Defaults to 1.

    Methods:
        distance: Computes the distance between two functions using the Sobolev norm.
        distances: Computes pairwise distances between two lists of functions.
        check_non_negativity: Verifies the non-negativity axiom of the metric.
        check_identity: Verifies the identity of indiscernibles axiom of the metric.
        check_symmetry: Verifies the symmetry axiom of the metric.
        check_triangle_inequality: Verifies the triangle inequality axiom of the metric.
    """

    type: Literal["SobolevMetric"] = "SobolevMetric"
    order: int

    def __init__(self, order: int = 1, **kwargs):
        """
        Initializes the SobolevMetric instance with the specified order of derivatives.

        Args:
            order: The highest order of derivatives to include in the metric computation.
            **kwargs: Additional keyword arguments passed to the base class.
        """
        super().__init__(**kwargs)
        self.order = order

    def distance(
        self, x: Union[Callable, list, float], y: Union[Callable, list, float]
    ) -> float:
        """
        Computes the distance between two functions using the Sobolev norm.

        The distance is calculated as the Sobolev norm of the difference between the two functions.

        Args:
            x: The first function or point.
            y: The second function or point.

        Returns:
            float: The computed distance between x and y.

        Raises:
            MetricViolationError: If any metric axiom is violated.
        """
        logger.debug(f"Calculating Sobolev distance between {x} and {y}")

        # Compute the difference between the two functions
        if callable(x) and callable(y):

            def difference_func(*args):
                return x(*args) - y(*args)
        else:
            difference_func = x - y

        # Compute the Sobolev norm of the difference
        sobolev_norm = SobolevNorm(order=self.order)
        distance = sobolev_norm.compute(difference_func)

        return distance

    def distances(
        self,
        xs: List[Union[Callable, list, float]],
        ys: List[Union[Callable, list, float]],
    ) -> List[List[float]]:
        """
        Computes pairwise distances between two lists of functions.

        Args:
            xs: First list of functions or points.
            ys: Second list of functions or points.

        Returns:
            List[List[float]]: Matrix of pairwise distances between points in xs and ys.
        """
        logger.debug(
            f"Calculating pairwise Sobolev distances between {len(xs)} points and {len(ys)} points"
        )

        return [[self.distance(x, y) for y in ys] for x in xs]

    def check_non_negativity(
        self, x: Union[Callable, list, float], y: Union[Callable, list, float]
    ) -> None:
        """
        Verifies the non-negativity axiom: d(x,y) ≥ 0.

        Args:
            x: First point.
            y: Second point.

        Raises:
            MetricViolationError: If d(x,y) < 0.
        """
        logger.debug("Checking non-negativity axiom")
        distance = self.distance(x, y)
        if distance < 0:
            raise MetricViolationError("Non-negativity axiom violated: d(x,y) < 0")

    def check_identity(
        self, x: Union[Callable, list, float], y: Union[Callable, list, float]
    ) -> None:
        """
        Verifies the identity of indiscernibles axiom: d(x,y) = 0 if and only if x = y.

        Args:
            x: First point.
            y: Second point.

        Raises:
            MetricViolationError: If d(x,y) = 0 but x ≠ y, or d(x,y) ≠ 0 but x = y.
        """
        logger.debug("Checking identity of indiscernibles axiom")
        distance = self.distance(x, y)
        if x == y and distance != 0:
            raise MetricViolationError("Identity axiom violated: x = y but d(x,y) ≠ 0")
        if x != y and distance == 0:
            raise MetricViolationError("Identity axiom violated: x ≠ y but d(x,y) = 0")

    def check_symmetry(
        self, x: Union[Callable, list, float], y: Union[Callable, list, float]
    ) -> None:
        """
        Verifies the symmetry axiom: d(x,y) = d(y,x).

        Args:
            x: First point.
            y: Second point.

        Raises:
            MetricViolationError: If d(x,y) ≠ d(y,x).
        """
        logger.debug("Checking symmetry axiom")
        distance_xy = self.distance(x, y)
        distance_yx = self.distance(y, x)
        if distance_xy != distance_yx:
            raise MetricViolationError("Symmetry axiom violated: d(x,y) ≠ d(y,x)")

    def check_triangle_inequality(
        self,
        x: Union[Callable, list, float],
        y: Union[Callable, list, float],
        z: Union[Callable, list, float],
    ) -> None:
        """
        Verifies the triangle inequality axiom: d(x,z) ≤ d(x,y) + d(y,z).

        Args:
            x: First point.
            y: Second point.
            z: Third point.

        Raises:
            MetricViolationError: If d(x,z) > d(x,y) + d(y,z).
        """
        logger.debug("Checking triangle inequality axiom")
        distance_xz = self.distance(x, z)
        distance_xy = self.distance(x, y)
        distance_yz = self.distance(y, z)

        if distance_xz > distance_xy + distance_yz:
            raise MetricViolationError(
                "Triangle inequality violated: d(x,z) > d(x,y) + d(y,z)"
            )
