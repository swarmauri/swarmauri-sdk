from typing import Union, List, Sequence, Callable, Optional
import math
import logging

from swarmauri_base.metrics import MetricBase
from swarmauri_standard.norms import L2EuclideanNorm

logger = logging.getLogger(__name__)


@MetricBase.register_type(MetricBase, "EuclideanMetric")
class EuclideanMetric(MetricBase):
    """
    A concrete implementation of the MetricBase class that computes the standard
    Euclidean (L2) distance between vectors.

    Inherits from:
        MetricBase: Base class providing template logic for metric computations.

    Attributes:
        type: String identifier for the metric type.

    Methods:
        distance: Computes the Euclidean distance between two vectors.
        distances: Computes pairwise distances between two lists of vectors.
        check_non_negativity: Verifies the non-negativity axiom.
        check_identity: Verifies the identity of indiscernibles axiom.
        check_symmetry: Verifies the symmetry axiom.
        check_triangle_inequality: Verifies the triangle inequality axiom.
    """

    type: str = "EuclideanMetric"

    def __init__(self):
        """
        Initializes the EuclideanMetric instance with the L2 norm.
        """
        self.norm = L2EuclideanNorm()

    def distance(
        self, x: Union[Sequence[float], Callable], y: Union[Sequence[float], Callable]
    ) -> float:
        """
        Computes the Euclidean (L2) distance between two vectors.

        Args:
            x: First vector
            y: Second vector

        Returns:
            float: The Euclidean distance between x and y

        Raises:
            ValueError: If the input vectors have different dimensions
        """
        logger.debug(f"Calculating Euclidean distance between {x} and {y}")

        # Ensure vectors are of the same dimension
        if len(x) != len(y):
            raise ValueError("Input vectors must have the same dimension")

        # Compute the difference vector
        difference = [x[i] - y[i] for i in range(len(x))]

        # Compute the L2 norm of the difference vector
        return self.norm.compute(difference)

    def distances(
        self,
        xs: List[Union[Sequence[float], Callable]],
        ys: List[Union[Sequence[float], Callable]],
    ) -> List[List[float]]:
        """
        Computes pairwise Euclidean distances between two lists of vectors.

        Args:
            xs: List of first vectors
            ys: List of second vectors

        Returns:
            List[List[float]]: Matrix of pairwise distances where distances[i][j] is the distance between xs[i] and ys[j]

        Raises:
            ValueError: If any pair of vectors have different dimensions
        """
        logger.debug(
            f"Calculating pairwise distances between {len(xs)} vectors and {len(ys)} vectors"
        )

        distances = []
        for x in xs:
            row = []
            for y in ys:
                if len(x) != len(y):
                    raise ValueError("All input vectors must have the same dimension")
                row.append(self.distance(x, y))
            distances.append(row)
        return distances

    def check_non_negativity(
        self, x: Union[Sequence[float], Callable], y: Union[Sequence[float], Callable]
    ) -> None:
        """
        Verifies the non-negativity axiom: d(x,y) ≥ 0.

        Args:
            x: First vector
            y: Second vector

        Raises:
            ValueError: If the distance is negative
        """
        logger.debug("Checking non-negativity axiom")
        distance = self.distance(x, y)
        if distance < 0:
            raise ValueError(f"Non-negativity violation: distance was {distance}")

    def check_identity(
        self, x: Union[Sequence[float], Callable], y: Union[Sequence[float], Callable]
    ) -> None:
        """
        Verifies the identity of indiscernibles axiom: d(x,y) = 0 if and only if x = y.

        Args:
            x: First vector
            y: Second vector

        Raises:
            ValueError: If d(x,y) = 0 but x ≠ y, or d(x,y) ≠ 0 but x = y
        """
        logger.debug("Checking identity of indiscernibles axiom")
        distance = self.distance(x, y)
        if distance == 0:
            if x != y:
                raise ValueError("Identity violation: d(x,y) = 0 but x ≠ y")
        else:
            if x == y:
                raise ValueError("Identity violation: d(x,y) ≠ 0 but x = y")

    def check_symmetry(
        self, x: Union[Sequence[float], Callable], y: Union[Sequence[float], Callable]
    ) -> None:
        """
        Verifies the symmetry axiom: d(x,y) = d(y,x).

        Args:
            x: First vector
            y: Second vector

        Raises:
            ValueError: If d(x,y) ≠ d(y,x)
        """
        logger.debug("Checking symmetry axiom")
        d_xy = self.distance(x, y)
        d_yx = self.distance(y, x)
        if d_xy != d_yx:
            raise ValueError(f"Symmetry violation: d(x,y) = {d_xy}, d(y,x) = {d_yx}")

    def check_triangle_inequality(
        self,
        x: Union[Sequence[float], Callable],
        y: Union[Sequence[float], Callable],
        z: Union[Sequence[float], Callable],
    ) -> None:
        """
        Verifies the triangle inequality axiom: d(x,z) ≤ d(x,y) + d(y,z).

        Args:
            x: First vector
            y: Second vector
            z: Third vector

        Raises:
            ValueError: If d(x,z) > d(x,y) + d(y,z)
        """
        logger.debug("Checking triangle inequality axiom")
        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)
        if d_xz > d_xy + d_yz:
            raise ValueError(f"Triangle inequality violation: {d_xz} > {d_xy} + {d_yz}")

    def __str__(self) -> str:
        """
        Returns a string representation of the EuclideanMetric instance.
        """
        return f"EuclideanMetric()"

    def __repr__(self) -> str:
        """
        Returns a string representation of the EuclideanMetric instance.
        """
        return f"EuclideanMetric()"
