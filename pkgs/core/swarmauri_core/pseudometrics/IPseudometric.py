from abc import ABC, abstractmethod
from typing import Any, Union, Tuple, Optional, Literal, Type
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix
import logging

logger = logging.getLogger(__name__)


class IPseudometric(ABC):
    """
    Interface for pseudometric space. This provides a contract for implementing
    pseudometric structures that support non-negative distance functions which
    satisfy symmetry and triangle inequality but may not distinguish distinct
    points (d(x,y)=0 doesn't imply x=y).

    The interface enforces type safety and provides a consistent API for
    different pseudometric implementations. It includes checks for the pseudometric
    properties and supports various input types including vectors, matrices,
    sequences, strings, and callables.
    """

    @abstractmethod
    def distance(self, x: Union[IVector, IMatrix, str, Callable, Sequence[Any]], 
                  y: Union[IVector, IMatrix, str, Callable, Sequence[Any]]) -> float:
        """
        Calculate the distance between two elements in the pseudometric space.

        Args:
            x: The first element to measure distance from. Can be a vector, matrix,
               string, callable, or sequence.
            y: The second element to measure distance to. Must be of the same type
               as x or compatible.

        Returns:
            float: The non-negative distance between x and y.

        Raises:
            TypeError: If x and y are not of compatible types.
        """
        pass

    @abstractmethod
    def distances(self, x: Union[IVector, IMatrix, str, Callable, Sequence[Any]], 
                  y_list: Union[List[Union[IVector, IMatrix, str, Callable, Sequence[Any]]], 
                               Tuple[Union[IVector, IMatrix, str, Callable, Sequence[Any]]]]) -> List[float]:
        """
        Calculate distances from a single element to a list of elements in the
        pseudometric space.

        Args:
            x: The reference element to measure distances from. Can be a vector,
               matrix, string, callable, or sequence.
            y_list: A list or tuple of elements to measure distances to. All
                elements must be of the same type as x or compatible.

        Returns:
            List[float]: A list of non-negative distances from x to each element
                in y_list.

        Raises:
            TypeError: If x and elements in y_list are not of compatible types.
        """
        pass

    @abstractmethod
    def check_non_negativity(self, x: Union[IVector, IMatrix, str, Callable, Sequence[Any]], 
                             y: Union[IVector, IMatrix, str, Callable, Sequence[Any]]) -> bool:
        """
        Check if the distance satisfies non-negativity: d(x,y) ≥ 0.

        Args:
            x: The first element to check.
            y: The second element to check.

        Returns:
            bool: True if distance is non-negative, False otherwise.
        """
        pass

    @abstractmethod
    def check_symmetry(self, x: Union[IVector, IMatrix, str, Callable, Sequence[Any]], 
                      y: Union[IVector, IMatrix, str, Callable, Sequence[Any]]) -> bool:
        """
        Check if the distance satisfies symmetry: d(x,y) = d(y,x).

        Args:
            x: The first element to check.
            y: The second element to check.

        Returns:
            bool: True if distance is symmetric, False otherwise.
        """
        pass

    @abstractmethod
    def check_triangle_inequality(self, x: Union[IVector, IMatrix, str, Callable, Sequence[Any]], 
                                  y: Union[IVector, IMatrix, str, Callable, Sequence[Any]], 
                                  z: Union[IVector, IMatrix, str, Callable, Sequence[Any]]) -> bool:
        """
        Check if the distance satisfies triangle inequality: d(x,z) ≤ d(x,y) + d(y,z).

        Args:
            x: The first element to check.
            y: The second element to check.
            z: The third element to check.

        Returns:
            bool: True if triangle inequality holds, False otherwise.
        """
        pass

    @abstractmethod
    def check_weak_identity(self, x: Union[IVector, IMatrix, str, Callable, Sequence[Any]], 
                           y: Union[IVector, IMatrix, str, Callable, Sequence[Any]]) -> bool:
        """
        Check if the distance satisfies weak identity of indiscernibles:
        d(x,y) = 0 if and only if x and y are not distinguishable.

        Args:
            x: The first element to check.
            y: The second element to check.

        Returns:
            bool: True if weak identity holds, False otherwise.
        """
        pass