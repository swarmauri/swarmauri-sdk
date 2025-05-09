from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, Sequence, Tuple, TypeVar, Union
import logging

from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

# Configure logging
logger = logging.getLogger(__name__)

# Define type variables for input types
InputTypes = TypeVar('InputTypes', IVector, IMatrix, Sequence, str, Callable)
DistanceInput = TypeVar('DistanceInput', InputTypes, Iterable[InputTypes])

class IPseudometric(ABC):
    """
    Interface for pseudometric space. This interface defines a relaxed metric structure
    where the distance function is non-negative, symmetric, and satisfies the triangle
    inequality, but does not necessarily distinguish between distinct points.

    This interface provides methods for computing distances between points as well as
    validating the pseudometric properties.
    """

    @abstractmethod
    def distance(self, x: InputTypes, y: InputTypes) -> float:
        """
        Compute the distance between two points x and y.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point

        Returns:
            float:
                The distance between x and y

        Raises:
            TypeError:
                If x or y are not of supported types
        """
        pass

    @abstractmethod
    def distances(self, x: InputTypes, ys: Iterable[InputTypes]) -> Iterable[float]:
        """
        Compute distances from point x to multiple points ys.

        Args:
            x: InputTypes
                The reference point
            ys: Iterable[InputTypes]
                The collection of points to compute distances to

        Returns:
            Iterable[float]:
                An iterable of distances from x to each point in ys

        Raises:
            TypeError:
                If x or any element in ys are not of supported types
        """
        pass

    @abstractmethod
    def check_non_negativity(self, x: InputTypes, y: InputTypes) -> bool:
        """
        Check if the distance satisfies non-negativity.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point

        Returns:
            bool:
                True if distance(x, y) >= 0, False otherwise
        """
        pass

    @abstractmethod
    def check_symmetry(self, x: InputTypes, y: InputTypes) -> bool:
        """
        Check if the distance satisfies symmetry.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point

        Returns:
            bool:
                True if distance(x, y) == distance(y, x), False otherwise
        """
        pass

    @abstractmethod
    def check_triangle_inequality(self, x: InputTypes, y: InputTypes, z: InputTypes) -> bool:
        """
        Check if the distance satisfies the triangle inequality.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point
            z: InputTypes
                The third point

        Returns:
            bool:
                True if distance(x, z) <= distance(x, y) + distance(y, z), False otherwise
        """
        pass

    @abstractmethod
    def check_weak_identity(self, x: InputTypes, y: InputTypes) -> bool:
        """
        Check if the distance satisfies weak identity of indiscernibles.

        Args:
            x: InputTypes
                The first point
            y: InputTypes
                The second point

        Returns:
            bool:
                True if x == y implies distance(x, y) == 0, False otherwise
        """
        pass