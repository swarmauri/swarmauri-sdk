from typing import Union, List, Sequence, Callable
import logging
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

logger = logging.getLogger(__name__)


@MetricBase.register_type(MetricBase, "SupremumMetric")
class SupremumMetric(MetricBase):
    """
    A concrete implementation of the MetricBase class implementing the L∞ metric.

    This class provides the functionality to compute distances between points
    using the supremum norm, which measures the largest component difference
    between two vectors.

    Attributes:
        type: Identifier for the metric type
        resource: Type of resource this class represents

    Methods:
        distance: Computes the distance between two points
        distances: Computes pairwise distances between two lists of points
        check_non_negativity: Verifies the non-negativity axiom
        check_identity: Verifies the identity of indiscernibles axiom
        check_symmetry: Verifies the symmetry axiom
        check_triangle_inequality: Verifies the triangle inequality axiom
    """
    type: str = "SupremumMetric"
    resource: str = "metric"

    def __init__(self) -> None:
        """
        Initializes the SupremumMetric instance.
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def distance(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                 y: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Computes the distance between two points x and y using the L∞ metric.

        The L∞ metric is defined as the maximum absolute difference between
        corresponding components of the two points.

        Args:
            x: The first point to measure distance from
            y: The second point to measure distance to

        Returns:
            float: The distance between x and y

        Raises:
            ValueError: If the input vectors have different lengths
        """
        self.logger.debug(f"Calculating distance between {x} and {y}")
        
        # Convert inputs to sequences if necessary
        if not isinstance(x, Sequence):
            x = list(x)
        if not isinstance(y, Sequence):
            y = list(y)
            
        if len(x) != len(y):
            raise ValueError("Input vectors must have the same length")
            
        max_diff = max(abs(x_i - y_i) for x_i, y_i in zip(x, y))
        self.logger.debug(f"Computed distance: {max_diff}")
        return max_diff

    def distances(self, xs: List[Union[IVector, IMatrix, Sequence, str, Callable]], 
                  ys: List[Union[IVector, IMatrix, Sequence, str, Callable]]) -> List[List[float]]:
        """
        Computes pairwise distances between two lists of points.

        Args:
            xs: First list of points
            ys: Second list of points

        Returns:
            List[List[float]]: Matrix of pairwise distances between points in xs and ys
        """
        self.logger.debug(f"Calculating pairwise distances between {len(xs)} points and {len(ys)} points")
        
        distance_matrix = []
        for x in xs:
            row = []
            for y in ys:
                row.append(self.distance(x, y))
            distance_matrix.append(row)
            
        self.logger.debug(f"Computed pairwise distances: {distance_matrix}")
        return distance_matrix

    def check_non_negativity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                            y: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Verifies the non-negativity axiom: d(x,y) ≥ 0.

        Args:
            x: First point
            y: Second point

        Raises:
            ValueError: If the distance is negative
        """
        self.logger.debug("Checking non-negativity axiom")
        distance = self.distance(x, y)
        if distance < 0:
            raise ValueError("Distance cannot be negative")

    def check_identity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                      y: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Verifies the identity of indiscernibles axiom: d(x,y) = 0 if and only if x = y.

        Args:
            x: First point
            y: Second point

        Raises:
            ValueError: If d(x,y) = 0 but x ≠ y, or d(x,y) ≠ 0 but x = y
        """
        self.logger.debug("Checking identity of indiscernibles axiom")
        if x == y:
            if self.distance(x, y) != 0:
                raise ValueError("Identity axiom violated: x == y but distance != 0")
        else:
            if self.distance(x, y) == 0:
                raise ValueError("Identity axiom violated: x != y but distance == 0")

    def check_symmetry(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                     y: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Verifies the symmetry axiom: d(x,y) = d(y,x).

        Args:
            x: First point
            y: Second point

        Raises:
            ValueError: If d(x,y) ≠ d(y,x)
        """
        self.logger.debug("Checking symmetry axiom")
        if self.distance(x, y) != self.distance(y, x):
            raise ValueError("Symmetry axiom violated: d(x,y) != d(y,x)")

    def check_triangle_inequality(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                                 y: Union[IVector, IMatrix, Sequence, str, Callable], 
                                 z: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Verifies the triangle inequality axiom: d(x,z) ≤ d(x,y) + d(y,z).

        Args:
            x: First point
            y: Second point
            z: Third point

        Raises:
            ValueError: If the triangle inequality is violated
        """
        self.logger.debug("Checking triangle inequality axiom")
        if self.distance(x, z) > self.distance(x, y) + self.distance(y, z):
            raise ValueError("Triangle inequality violated: d(x,z) > d(x,y) + d(y,z)")