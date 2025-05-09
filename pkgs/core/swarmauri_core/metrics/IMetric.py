from abc import ABC, abstractmethod
from typing import Any, Callable, Sequence, TypeVar, Union
import logging

from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T', IVector, IMatrix, Sequence, str, Callable)
S = TypeVar('S', int, float, bool, str)

class IMetric(ABC):
    """
    Interface for metric spaces. This class defines the core functionality required 
    for implementing metric spaces. It enforces the four main metric axioms:
    - Non-negativity: d(x, y) ≥ 0
    - Identity of indiscernibles: d(x, y) = 0 if and only if x = y
    - Symmetry: d(x, y) = d(y, x)
    - Triangle inequality: d(x, z) ≤ d(x, y) + d(y, z)

    All implementations must provide concrete implementations for the required methods.
    """

    @abstractmethod
    def distance(self, x: T, y: T) -> float:
        """
        Compute the distance between two points.

        Args:
            x: T
                The first point to compare
            y: T
                The second point to compare

        Returns:
            float:
                The computed distance between x and y

        Raises:
            ValueError:
                If the input types are not supported
            TypeError:
                If the input types are incompatible
        """
        raise NotImplementedError("distance must be implemented by subclass")

    @abstractmethod
    def distances(self, x: T, y_list: Union[T, Sequence[T]]) -> Union[float, Sequence[float]]:
        """
        Compute the distance(s) between a point and one or more points.

        Args:
            x: T
                The reference point
            y_list: Union[T, Sequence[T]]
                Either a single point or a sequence of points

        Returns:
            Union[float, Sequence[float]]:
                - If y_list is a single point: Returns the distance as a float
                - If y_list is a sequence: Returns a sequence of distances

        Raises:
            ValueError:
                If the input types are not supported
            TypeError:
                If the input types are incompatible
        """
        raise NotImplementedError("distances must be implemented by subclass")

    @abstractmethod
    def check_non_negativity(self, x: T, y: T) -> bool:
        """
        Verify the non-negativity axiom: d(x, y) ≥ 0.

        Args:
            x: T
                The first point
            y: T
                The second point

        Returns:
            bool:
                True if the non-negativity condition holds, False otherwise

        Raises:
            ValueError:
                If the distance computation fails
        """
        raise NotImplementedError("check_non_negativity must be implemented by subclass")

    @abstractmethod
    def check_identity(self, x: T, y: T) -> bool:
        """
        Verify the identity of indiscernibles axiom: d(x, y) = 0 if and only if x = y.

        Args:
            x: T
                The first point
            y: T
                The second point

        Returns:
            bool:
                True if the identity condition holds, False otherwise

        Raises:
            ValueError:
                If the distance computation fails
        """
        raise NotImplementedError("check_identity must be implemented by subclass")

    @abstractmethod
    def check_symmetry(self, x: T, y: T) -> bool:
        """
        Verify the symmetry axiom: d(x, y) = d(y, x).

        Args:
            x: T
                The first point
            y: T
                The second point

        Returns:
            bool:
                True if the symmetry condition holds, False otherwise

        Raises:
            ValueError:
                If the distance computation fails
        """
        raise NotImplementedError("check_symmetry must be implemented by subclass")

    @abstractmethod
    def check_triangle_inequality(self, x: T, y: T, z: T) -> bool:
        """
        Verify the triangle inequality axiom: d(x, z) ≤ d(x, y) + d(y, z).

        Args:
            x: T
                The first point
            y: T
                The second point
            z: T
                The third point

        Returns:
            bool:
                True if the triangle inequality condition holds, False otherwise

        Raises:
            ValueError:
                If the distance computation fails
        """
        raise NotImplementedError("check_triangle_inequality must be implemented by subclass")

    def __init__(self):
        """
        Initialize the metric instance.
        """
        logger.debug("IMetric instance initialized")