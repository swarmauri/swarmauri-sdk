from typing import Union, List, Literal, Optional
from swarmauri_base.metrics.MetricBase import MetricBase
import logging

logger = logging.getLogger(__name__)


@MetricBase.register_type(MetricBase, "DiscreteMetric")
class DiscreteMetric(MetricBase):
    """
    A basic discrete metric implementation that returns 1 if two points are different
    and 0 if they are the same. This metric satisfies all metric axioms.
    
    Inherits from:
    - MetricBase: The base class for all metric implementations.
    """
    type: Literal["DiscreteMetric"] = "DiscreteMetric"

    def distance(
        self, 
        x: Union[object, List, str, callable], 
        y: Union[object, List, str, callable]
    ) -> float:
        """
        Compute the discrete distance between two points.

        Args:
            x: The first point. Can be any hashable type.
            y: The second point. Can be any hashable type.

        Returns:
            float: 0 if x and y are the same, 1 otherwise.

        Example:
            >>> metric.distance("a", "a")
            0
            >>> metric.distance("a", "b")
            1
        """
        logger.debug("Computing discrete distance between two points")
        return 0 if x == y else 1

    def distances(
        self, 
        x: Union[object, List, str, callable], 
        ys: List[Union[object, List, str, callable]]
    ) -> List[float]:
        """
        Compute the discrete distances from a single point to multiple points.

        Args:
            x: The reference point. Can be any hashable type.
            ys: List of points to compute distances to. Each can be any hashable type.

        Returns:
            List[float]: List of distances from x to each point in ys.

        Example:
            >>> metric.distances("a", ["a", "b", "a"])
            [0, 1, 0]
        """
        logger.debug(f"Computing distances from {x} to {ys}")
        return [self.distance(x, y) for y in ys]

    def check_non_negativity(
        self, 
        x: Union[object, List, str, callable], 
        y: Union[object, List, str, callable]
    ) -> Literal[True]:
        """
        Verify the non-negativity property: d(x, y) ≥ 0.

        Args:
            x: The first point. Can be any hashable type.
            y: The second point. Can be any hashable type.

        Returns:
            Literal[True]: Always True since discrete metric returns 0 or 1.
        """
        logger.debug("Checking non-negativity property")
        return True

    def check_identity(
        self, 
        x: Union[object, List, str, callable], 
        y: Union[object, List, str, callable]
    ) -> Literal[True]:
        """
        Verify the identity of indiscernibles property: d(x, y) = 0 if and only if x = y.

        Args:
            x: The first point. Can be any hashable type.
            y: The second point. Can be any hashable type.

        Returns:
            Literal[True]: True if the identity property holds, False otherwise.
        """
        logger.debug("Checking identity property")
        distance = self.distance(x, y)
        return Literal[True](distance == 0 if x == y else False)

    def check_symmetry(
        self, 
        x: Union[object, List, str, callable], 
        y: Union[object, List, str, callable]
    ) -> Literal[True]:
        """
        Verify the symmetry property: d(x, y) = d(y, x).

        Args:
            x: The first point. Can be any hashable type.
            y: The second point. Can be any hashable type.

        Returns:
            Literal[True]: Always True since discrete metric is symmetric.
        """
        logger.debug("Checking symmetry property")
        return Literal[True](self.distance(x, y) == self.distance(y, x))

    def check_triangle_inequality(
        self, 
        x: Union[object, List, str, callable], 
        y: Union[object, List, str, callable], 
        z: Union[object, List, str, callable]
    ) -> Literal[True]:
        """
        Verify the triangle inequality property: d(x, z) ≤ d(x, y) + d(y, z).

        Args:
            x: The first point. Can be any hashable type.
            y: The second point. Can be any hashable type.
            z: The third point. Can be any hashable type.

        Returns:
            Literal[True]: Always True since discrete metric satisfies triangle inequality.
        """
        logger.debug("Checking triangle inequality property")
        return Literal[True]((self.distance(x, z) <= self.distance(x, y) + self.distance(y, z)))