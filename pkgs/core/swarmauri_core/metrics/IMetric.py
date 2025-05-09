from abc import ABC, abstractmethod
from typing import Any, Union, List, Tuple, Literal
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix
import logging

logger = logging.getLogger(__name__)


class IMetric(ABC):
    """
    Interface for metric spaces. This interface defines the contract for 
    implementing metric spaces that satisfy the metric axioms:

    1. Point separation (also called identity of indiscernibles)
    2. Symmetry
    3. Triangle inequality
    4. Non-negativity

    All implementations must adhere to these axioms and provide implementations
    for the required methods.
    """

    @abstractmethod
    def distance(
        self, 
        x: Union[IVector, IMatrix, List, str, callable], 
        y: Union[IVector, IMatrix, List, str, callable]
    ) -> float:
        """
        Compute the distance between two points.

        Args:
            x: The first point. Can be a vector, matrix, list, string, or callable.
            y: The second point. Can be a vector, matrix, list, string, or callable.

        Returns:
            float: The computed distance between x and y.

        Raises:
            TypeError: If input types are not supported.
            ValueError: If inputs are invalid or incompatible.
        """
        pass

    @abstractmethod
    def distances(
        self, 
        x: Union[IVector, IMatrix, List, str, callable], 
        ys: List[Union[IVector, IMatrix, List, str, callable]]
    ) -> List[float]:
        """
        Compute distances from a single point to multiple points.

        Args:
            x: The reference point. Can be a vector, matrix, list, string, or callable.
            ys: List of points to compute distances to. Each can be a vector, 
                matrix, list, string, or callable.

        Returns:
            List[float]: List of distances from x to each point in ys.

        Raises:
            TypeError: If input types are not supported.
            ValueError: If inputs are invalid or incompatible.
        """
        pass

    @abstractmethod
    def check_non_negativity(
        self, 
        x: Union[IVector, IMatrix, List, str, callable], 
        y: Union[IVector, IMatrix, List, str, callable]
    ) -> Literal[True]:
        """
        Verify the non-negativity property: d(x, y) ≥ 0.

        Args:
            x: The first point. Can be a vector, matrix, list, string, or callable.
            y: The second point. Can be a vector, matrix, list, string, or callable.

        Returns:
            Literal[True]: True if the non-negativity property holds.

        Raises:
            ValueError: If the non-negativity property does not hold.
        """
        pass

    @abstractmethod
    def check_identity(
        self, 
        x: Union[IVector, IMatrix, List, str, callable], 
        y: Union[IVector, IMatrix, List, str, callable]
    ) -> Literal[True]:
        """
        Verify the identity of indiscernibles property: d(x, y) = 0 if and only if x = y.

        Args:
            x: The first point. Can be a vector, matrix, list, string, or callable.
            y: The second point. Can be a vector, matrix, list, string, or callable.

        Returns:
            Literal[True]: True if the identity property holds.

        Raises:
            ValueError: If the identity property does not hold.
        """
        pass

    @abstractmethod
    def check_symmetry(
        self, 
        x: Union[IVector, IMatrix, List, str, callable], 
        y: Union[IVector, IMatrix, List, str, callable]
    ) -> Literal[True]:
        """
        Verify the symmetry property: d(x, y) = d(y, x).

        Args:
            x: The first point. Can be a vector, matrix, list, string, or callable.
            y: The second point. Can be a vector, matrix, list, string, or callable.

        Returns:
            Literal[True]: True if the symmetry property holds.

        Raises:
            ValueError: If the symmetry property does not hold.
        """
        pass

    @abstractmethod
    def check_triangle_inequality(
        self, 
        x: Union[IVector, IMatrix, List, str, callable], 
        y: Union[IVector, IMatrix, List, str, callable], 
        z: Union[IVector, IMatrix, List, str, callable]
    ) -> Literal[True]:
        """
        Verify the triangle inequality property: d(x, z) ≤ d(x, y) + d(y, z).

        Args:
            x: The first point. Can be a vector, matrix, list, string, or callable.
            y: The second point. Can be a vector, matrix, list, string, or callable.
            z: The third point. Can be a vector, matrix, list, string, or callable.

        Returns:
            Literal[True]: True if the triangle inequality property holds.

        Raises:
            ValueError: If the triangle inequality property does not hold.
        """
        pass