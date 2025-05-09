from typing import Callable, Sequence, Union, List, Optional
import logging

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.metrics.IMetric import MetricViolationError
from swarmauri_core.vectors.IVector import IVector

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "DiscreteMetric")
class DiscreteMetric(MetricBase):
    """
    A basic binary metric implementation that returns 1 if two points are different
    and 0 if they are the same. This metric works with any hashable types.
    """

    type: str = "DiscreteMetric"
    resource: Optional[str] = "DiscreteMetric"

    def distance(
        self,
        x: Union[IVector, IMatrix, Sequence, str, Callable],
        y: Union[IVector, IMatrix, Sequence, str, Callable],
    ) -> float:
        """
        Computes the distance between two points x and y. Returns 1 if x and y are different,
        and 0 if they are the same.

        Args:
            x: The first point to measure distance from
            y: The second point to measure distance to

        Returns:
            float: 0 if x == y, 1 otherwise
        """
        logger.debug(f"Calculating discrete distance between {x} and {y}")
        return 0.0 if x == y else 1.0

    def distances(
        self,
        xs: List[Union[IVector, IMatrix, Sequence, str, Callable]],
        ys: List[Union[IVector, IMatrix, Sequence, str, Callable]],
    ) -> List[List[float]]:
        """
        Computes pairwise distances between two lists of points.

        Args:
            xs: First list of points
            ys: Second list of points

        Returns:
            List[List[float]]: Matrix where each element [i][j] is 0 if xs[i] == ys[j], otherwise 1
        """
        logger.debug(
            f"Calculating pairwise discrete distances between {len(xs)} points and {len(ys)} points"
        )
        return [[0.0 if x == y else 1.0 for y in ys] for x in xs]

    def check_non_negativity(
        self,
        x: Union[IVector, IMatrix, Sequence, str, Callable],
        y: Union[IVector, IMatrix, Sequence, str, Callable],
    ) -> None:
        """
        Verifies the non-negativity axiom: d(x,y) ≥ 0.

        Args:
            x: First point
            y: Second point

        Raises:
            MetricViolationError: If distance is negative
        """
        distance = self.distance(x, y)
        if distance < 0:
            raise MetricViolationError(
                f"Non-negativity violated: distance({x}, {y}) = {distance}"
            )

    def check_identity(
        self,
        x: Union[IVector, IMatrix, Sequence, str, Callable],
        y: Union[IVector, IMatrix, Sequence, str, Callable],
    ) -> None:
        """
        Verifies the identity of indiscernibles axiom: d(x,y) = 0 if and only if x = y.

        Args:
            x: First point
            y: Second point

        Raises:
            MetricViolationError: If axiom is violated
        """
        distance = self.distance(x, y)
        if (x == y and distance != 0) or (x != y and distance == 0):
            raise MetricViolationError(
                f"Identity axiom violated: {x} and {y} have distance {distance}"
            )

    def check_symmetry(
        self,
        x: Union[IVector, IMatrix, Sequence, str, Callable],
        y: Union[IVector, IMatrix, Sequence, str, Callable],
    ) -> None:
        """
        Verifies the symmetry axiom: d(x,y) = d(y,x).

        Args:
            x: First point
            y: Second point

        Raises:
            MetricViolationError: If d(x,y) ≠ d(y,x)
        """
        distance_xy = self.distance(x, y)
        distance_yx = self.distance(y, x)
        if distance_xy != distance_yx:
            raise MetricViolationError(
                f"Symmetry violated: d({x}, {y}) = {distance_xy}, d({y}, {x}) = {distance_yx}"
            )

    def check_triangle_inequality(
        self,
        x: Union[IVector, IMatrix, Sequence, str, Callable],
        y: Union[IVector, IMatrix, Sequence, str, Callable],
        z: Union[IVector, IMatrix, Sequence, str, Callable],
    ) -> None:
        """
        Verifies the triangle inequality axiom: d(x,z) ≤ d(x,y) + d(y,z).

        Args:
            x: First point
            y: Second point
            z: Third point

        Raises:
            MetricViolationError: If d(x,z) > d(x,y) + d(y,z)
        """
        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)

        if d_xz > d_xy + d_yz:
            raise MetricViolationError(
                f"Triangle inequality violated: d({x}, {z}) = {d_xz}, d({x}, {y}) + d({y}, {z}) = {d_xy + d_yz}"
            )
