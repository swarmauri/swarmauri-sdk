from abc import ABC, abstractmethod
from typing import Union, List, Sequence, Callable
import logging

from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

logger = logging.getLogger(__name__)


class MetricViolationError(Exception):
    """Raised when a metric space axiom is violated."""
    pass


class IMetric(ABC):
    """
    Interface for metric spaces. This class defines the contract for proper metric spaces
    by enforcing the four main metric axioms: point separation, symmetry, triangle
    inequality, and non-negativity.

    Methods:
        distance: Computes the distance between two points
        distances: Computes pairwise distances between two lists of points
        check_non_negativity: Verifies the non-negativity axiom
        check_identity: Verifies the identity of indiscernibles axiom
        check_symmetry: Verifies the symmetry axiom
        check_triangle_inequality: Verifies the triangle inequality axiom
    """

    @abstractmethod
    def distance(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Computes the distance between two points x and y.

        Args:
            x: The first point to measure distance from
            y: The second point to measure distance to

        Returns:
            float: The distance between x and y

        Raises:
            MetricViolationError: If any metric axiom is violated
        """
        logger.debug(f"Calculating distance between {x} and {y}")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def distances(self, xs: List[Union[IVector, IMatrix, Sequence, str, Callable]], ys: List[Union[IVector, IMatrix, Sequence, str, Callable]]) -> List[List[float]]:
        """
        Computes pairwise distances between two lists of points.

        Args:
            xs: First list of points
            ys: Second list of points

        Returns:
            List[List[float]]: Matrix of pairwise distances between points in xs and ys

        Raises:
            MetricViolationError: If any metric axiom is violated
        """
        logger.debug(f"Calculating pairwise distances between {len(xs)} points and {len(ys)} points")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def check_non_negativity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Verifies the non-negativity axiom: d(x,y) ≥ 0.

        Args:
            x: First point
            y: Second point

        Raises:
            MetricViolationError: If d(x,y) < 0
        """
        d = self.distance(x, y)
        if d < 0:
            logger.error(f"Non-negativity violated: d({x}, {y}) = {d}")
            raise MetricViolationError(f"Non-negativity violation: d({x}, {y}) = {d}")

    @abstractmethod
    def check_identity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Verifies the identity of indiscernibles axiom: d(x,y) = 0 if and only if x = y.

        Args:
            x: First point
            y: Second point

        Raises:
            MetricViolationError: If d(x,y) = 0 but x ≠ y, or d(x,y) ≠ 0 but x = y
        """
        d = self.distance(x, y)
        if d == 0 and x != y:
            logger.error(f"Identity violation: d({x}, {y}) = 0 but x ≠ y")
            raise MetricViolationError(f"Identity violation: d({x}, {y}) = 0 but x ≠ y")
        elif d != 0 and x == y:
            logger.error(f"Identity violation: d({x}, {y}) ≠ 0 but x = y")
            raise MetricViolationError(f"Identity violation: d({x}, {y}) ≠ 0 but x = y")

    @abstractmethod
    def check_symmetry(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Verifies the symmetry axiom: d(x,y) = d(y,x).

        Args:
            x: First point
            y: Second point

        Raises:
            MetricViolationError: If d(x,y) ≠ d(y,x)
        """
        d_xy = self.distance(x, y)
        d_yx = self.distance(y, x)
        if d_xy != d_yx:
            logger.error(f"Symmetry violation: d({x}, {y}) = {d_xy} ≠ {d_yx} = d({y}, {x})")
            raise MetricViolationError(f"Symmetry violation: d({x}, {y}) ≠ d({y}, {x})")

    @abstractmethod
    def check_triangle_inequality(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable], z: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
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
            logger.error(f"Triangle inequality violation: d({x}, {z}) = {d_xz} > {d_xy} + {d_yz} = d({x}, {y}) + d({y}, {z})")
            raise MetricViolationError(f"Triangle inequality violation: d({x}, {z}) > d({x}, {y}) + d({y}, {z})")