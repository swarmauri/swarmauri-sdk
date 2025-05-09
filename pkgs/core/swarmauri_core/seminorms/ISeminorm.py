from abc import ABC, abstractmethod
from typing import Union, Sequence, Callable
import logging
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

logger = logging.getLogger(__name__)


class ISeminorm(ABC):
    """
    Interface for seminorm structures. This interface defines the fundamental
    operations and properties that must be implemented by any seminorm
    implementation. A seminorm relaxes the definiteness property of norms,
    allowing for the possibility that the seminorm of an object is zero even
    if the object itself is not trivial.

    Implementations of this interface must provide concrete implementations
    for all defined methods. The interface enforces type safety through
    type annotations and abstract method definitions.
    """

    @abstractmethod
    def compute(
        self,
        input: Union[IVector, IMatrix, Sequence, str, Callable]
    ) -> float:
        """
        Compute the seminorm of the given input.

        Args:
            input: The input to compute the seminorm for. Can be a vector,
                matrix, sequence, string, or callable object.

        Returns:
            float: The computed seminorm value.

        Raises:
            ValueError: If the input type is not supported.
            TypeError: If the input is of incorrect type.
        """
        pass

    @abstractmethod
    def check_triangle_inequality(
        self,
        a: Union[IVector, IMatrix, Sequence, str, Callable],
        b: Union[IVector, IMatrix, Sequence, str, Callable]
    ) -> bool:
        """
        Check if the triangle inequality holds for the given inputs.

        The triangle inequality states that for any elements a and b,
        the seminorm of (a + b) should be less than or equal to the sum
        of the seminorms of a and b.

        Args:
            a: The first element to check.
            b: The second element to check.

        Returns:
            bool: True if the triangle inequality holds, False otherwise.
        """
        pass

    @abstractmethod
    def check_scalar_homogeneity(
        self,
        input: Union[IVector, IMatrix, Sequence, str, Callable],
        scalar: float
    ) -> bool:
        """
        Check if the seminorm satisfies scalar homogeneity.

        Scalar homogeneity requires that for any scalar c and input x,
        the seminorm of (c * x) is equal to |c| * seminorm(x).

        Args:
            input: The input element to check.
            scalar: The scalar to scale the input by.

        Returns:
            bool: True if scalar homogeneity holds, False otherwise.
        """
        pass