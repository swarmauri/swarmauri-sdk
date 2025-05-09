from abc import ABC, abstractmethod
from typing import Union, Sequence, Callable, Tuple, List, Any
import logging
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

logger = logging.getLogger(__name__)


class IPseudometric(ABC):
    """
    Interface for pseudometric space structure.

    This interface defines the basic structure and operations for working with
    pseudometric spaces in various applications, such as machine learning,
    information retrieval, and similarity search.

    A pseudometric satisfies the following properties:
    1. Non-negativity: d(x, y) ≥ 0
    2. Symmetry: d(x, y) = d(y, x)
    3. Triangle inequality: d(x, z) ≤ d(x, y) + d(y, z)
    4. Weak identity: d(x, y) = 0 if x = y (but not necessarily vice versa)

    Implementations should provide concrete distance calculations for various
    data types including vectors, matrices, sequences, strings, and callables.
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def distance(self, x: Union[IVector, IMatrix, Sequence, str, Callable],
                  y: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Computes the pseudometric distance between two elements.

        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first element to compute distance between
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second element to compute distance between

        Returns:
            float: The computed pseudometric distance
        """
        raise NotImplementedError("distance method must be implemented")

    @abstractmethod
    def distances(self, xs: Sequence[Union[IVector, IMatrix, Sequence, str, Callable]],
                   ys: Sequence[Union[IVector, IMatrix, Sequence, str, Callable]]) -> List[float]:
        """
        Computes pairwise pseudometric distances between two sequences of elements.

        Args:
            xs: Sequence[Union[IVector, IMatrix, Sequence, str, Callable]]
                The first sequence of elements
            ys: Sequence[Union[IVector, IMatrix, Sequence, str, Callable]]
                The second sequence of elements

        Returns:
            List[float]: A list of computed pseudometric distances
        """
        raise NotImplementedError("distances method must be implemented")

    def check_non_negativity(self, x: Union[IVector, IMatrix, Sequence, str, Callable],
                             y: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Checks if the distance satisfies the non-negativity property.

        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first element to check
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second element to check

        Raises:
            ValueError: If non-negativity property is violated
        """
        distance = self.distance(x, y)
        if distance < 0:
            self.logger.error(f"Non-negativity violated: d({x}, {y}) = {distance}")
            raise ValueError(f"Non-negativity violated: d({x}, {y}) = {distance}")

    def check_symmetry(self, x: Union[IVector, IMatrix, Sequence, str, Callable],
                       y: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Checks if the distance satisfies the symmetry property.

        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first element to check
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second element to check

        Raises:
            ValueError: If symmetry property is violated
        """
        d_xy = self.distance(x, y)
        d_yx = self.distance(y, x)
        if not abs(d_xy - d_yx) < 1e-9:  # Allowing for floating-point precision
            self.logger.error(f"Symmetry violated: d({x}, {y}) = {d_xy}, d({y}, {x}) = {d_yx}")
            raise ValueError(f"Symmetry violated: d({x}, {y}) = {d_xy}, d({y}, {x}) = {d_yx}")

    def check_triangle_inequality(self,
                                   x: Union[IVector, IMatrix, Sequence, str, Callable],
                                   y: Union[IVector, IMatrix, Sequence, str, Callable],
                                   z: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Checks if the distance satisfies the triangle inequality property.

        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first element to check
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second element to check
            z: Union[IVector, IMatrix, Sequence, str, Callable]
                The third element to check

        Raises:
            ValueError: If triangle inequality property is violated
        """
        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)
        if d_xz > d_xy + d_yz:
            self.logger.error(f"Triangle inequality violated: d({x}, {z}) = {d_xz}, "
                             f"d({x}, {y}) + d({y}, {z}) = {d_xy + d_yz}")
            raise ValueError(f"Triangle inequality violated: d({x}, {z}) = {d_xz}, "
                             f"d({x}, {y}) + d({y}, {z}) = {d_xy + d_yz}")

    def check_weak_identity(self, x: Union[IVector, IMatrix, Sequence, str, Callable],
                            y: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Checks if the distance satisfies the weak identity property.

        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first element to check
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second element to check

        Raises:
            ValueError: If weak identity property is violated
        """
        if x != y:
            distance = self.distance(x, y)
            if distance == 0:
                self.logger.error(f"Weak identity violated: d({x}, {y}) = 0 but {x} != {y}")
                raise ValueError(f"Weak identity violated: d({x}, {y}) = 0 but {x} != {y}")