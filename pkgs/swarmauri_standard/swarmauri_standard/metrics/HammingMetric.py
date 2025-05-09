from typing import Union, List, Optional, Literal
from abc import ABC
import logging
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase, ResourceTypes
from swarmauri_core.metrics.IMetric import IMetric
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "HammingMetric")
class HammingMetric(MetricBase):
    """
    A concrete implementation of the MetricBase class that computes the Hamming distance.
    The Hamming distance between two sequences of equal length is the number of positions
    at which the corresponding symbols are different. This metric is suitable for binary
    data, bitwise operations, and categorical vectors.

    Inherits From:
        MetricBase: The base class for all metric implementations in the swarmauri framework.

    Attributes:
        type: Literal["HammingMetric"] = "HammingMetric": The type identifier for this metric.
        resource: Optional[str] = ResourceTypes.METRIC.value: The resource type identifier.

    Methods:
        distance: Computes the Hamming distance between two points.
        distances: Computes pairwise Hamming distances between two lists of points.
        check_non_negativity: Verifies the non-negativity axiom for the computed distances.
        check_identity: Verifies the identity of indiscernibles axiom for the computed distances.
        check_symmetry: Verifies the symmetry axiom for the computed distances.
        check_triangle_inequality: Verifies the triangle inequality axiom for the computed distances.
    """

    type: Literal["HammingMetric"] = "HammingMetric"
    resource: Optional[str] = ResourceTypes.METRIC.value

    def distance(
        self,
        x: Union[IVector, IMatrix, Sequence, str, Callable],
        y: Union[IVector, IMatrix, Sequence, str, Callable],
    ) -> float:
        """
        Computes the Hamming distance between two points x and y.

        Args:
            x: The first point to measure distance from
            y: The second point to measure distance to

        Returns:
            float: The Hamming distance between x and y

        Raises:
            ValueError: If the input sequences are not of equal length
        """
        logger.debug(f"Calculating Hamming distance between {x} and {y}")

        # Ensure inputs are of the same length
        if len(x) != len(y):
            raise ValueError("Input sequences must be of equal length")

        # Initialize distance counter
        distance = 0

        # Iterate through each pair of elements and count mismatches
        for x_elem, y_elem in zip(x, y):
            if x_elem != y_elem:
                distance += 1

        return distance

    def distances(
        self,
        xs: List[Union[IVector, IMatrix, Sequence, str, Callable]],
        ys: List[Union[IVector, IMatrix, Sequence, str, Callable]],
    ) -> List[List[float]]:
        """
        Computes pairwise Hamming distances between two lists of points.

        Args:
            xs: First list of points
            ys: Second list of points

        Returns:
            List[List[float]]: Matrix of pairwise Hamming distances between points in xs and ys

        Raises:
            ValueError: If any pair of points has different lengths
        """
        logger.debug(
            f"Calculating pairwise Hamming distances between {len(xs)} points and {len(ys)} points"
        )

        # Initialize the distance matrix
        distance_matrix = []

        # Iterate through each pair of points in xs and ys
        for x in xs:
            row = []
            for y in ys:
                # Calculate the distance for each pair
                row.append(self.distance(x, y))
            distance_matrix.append(row)

        return distance_matrix

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
            MetricViolationError: If d(x,y) < 0 (unlikely for Hamming distance)
        """
        logger.debug("Checking non-negativity axiom for Hamming metric")
        distance = self.distance(x, y)
        if distance < 0:
            raise MetricViolationError(
                f"Non-negativity violation: d({x}, {y}) = {distance} < 0"
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
            MetricViolationError: If d(x,y) = 0 but x ≠ y, or d(x,y) ≠ 0 but x = y
        """
        logger.debug("Checking identity of indiscernibles axiom for Hamming metric")
        distance = self.distance(x, y)
        if distance == 0 and x != y:
            raise MetricViolationError(
                f"Identity violation: d({x}, {y}) = 0 but {x} != {y}"
            )
        elif distance != 0 and x == y:
            raise MetricViolationError(
                f"Identity violation: d({x}, {y}) = {distance} but {x} == {y}"
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
        logger.debug("Checking symmetry axiom for Hamming metric")
        if self.distance(x, y) != self.distance(y, x):
            raise MetricViolationError(
                f"Symmetry violation: d({x}, {y}) = {self.distance(x, y)} ≠ {self.distance(y, x)} = d({y}, {x})"
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
        logger.debug("Checking triangle inequality axiom for Hamming metric")
        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)

        if d_xz > d_xy + d_yz:
            raise MetricViolationError(
                f"Triangle inequality violation: d({x}, {z}) = {d_xz} > {d_xy} + {d_yz} = d({x}, {y}) + d({y}, {z})"
            )
