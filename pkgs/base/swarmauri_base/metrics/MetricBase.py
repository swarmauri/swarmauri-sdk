from typing import Union, List, Sequence, Callable, Optional
from abc import abstractmethod
import logging

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.metrics.IMetric import IMetric
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class MetricBase(IMetric, ComponentBase):
    """
    A base implementation of the IMetric interface providing boilerplate code for
    metric spaces. This class implements all abstract methods but raises
    NotImplementedError, serving as a foundation for concrete metric
    implementations.
    """
    resource: Optional[str] = Field(default=ResourceTypes.METRIC.value)

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
            NotImplementedError: Since this is a base implementation
            MetricViolationError: If any metric axiom is violated
        """
        logger.debug(f"Calculating distance between {x} and {y}")
        raise NotImplementedError("This method must be implemented by a concrete subclass")

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
            NotImplementedError: Since this is a base implementation
            MetricViolationError: If any metric axiom is violated
        """
        logger.debug(f"Calculating pairwise distances between {len(xs)} points and {len(ys)} points")
        raise NotImplementedError("This method must be implemented by a concrete subclass")

    @abstractmethod
    def check_non_negativity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Verifies the non-negativity axiom: d(x,y) ≥ 0.

        Args:
            x: First point
            y: Second point

        Raises:
            NotImplementedError: Since this is a base implementation
            MetricViolationError: If d(x,y) < 0
        """
        logger.debug("Checking non-negativity axiom")
        raise NotImplementedError("This method must be implemented by a concrete subclass")

    @abstractmethod
    def check_identity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Verifies the identity of indiscernibles axiom: d(x,y) = 0 if and only if x = y.

        Args:
            x: First point
            y: Second point

        Raises:
            NotImplementedError: Since this is a base implementation
            MetricViolationError: If d(x,y) = 0 but x ≠ y, or d(x,y) ≠ 0 but x = y
        """
        logger.debug("Checking identity of indiscernibles axiom")
        raise NotImplementedError("This method must be implemented by a concrete subclass")

    @abstractmethod
    def check_symmetry(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Verifies the symmetry axiom: d(x,y) = d(y,x).

        Args:
            x: First point
            y: Second point

        Raises:
            NotImplementedError: Since this is a base implementation
            MetricViolationError: If d(x,y) ≠ d(y,x)
        """
        logger.debug("Checking symmetry axiom")
        raise NotImplementedError("This method must be implemented by a concrete subclass")

    @abstractmethod
    def check_triangle_inequality(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable], z: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Verifies the triangle inequality axiom: d(x,z) ≤ d(x,y) + d(y,z).

        Args:
            x: First point
            y: Second point
            z: Third point

        Raises:
            NotImplementedError: Since this is a base implementation
            MetricViolationError: If d(x,z) > d(x,y) + d(y,z)
        """
        logger.debug("Checking triangle inequality axiom")
        raise NotImplementedError("This method must be implemented by a concrete subclass")