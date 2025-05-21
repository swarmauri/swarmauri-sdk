from abc import ABC, abstractmethod
from typing import Callable, Literal, Sequence, TypeVar, Union

from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.vectors.IVector import IVector

T = TypeVar("T", bound=Union[int, float, complex])
InputType = Union[
    Literal[IVector], Literal[IMatrix], Sequence[T], str, Callable[..., T]
]


class ISeminorm(ABC):
    """
    Interface for seminorm structure.

    A seminorm is a function that assigns a non-negative length or size to all vectors
    in a vector space. Unlike a norm, a seminorm can have a null space that is larger
    than just the zero vector, meaning some non-zero vectors can have a seminorm of zero.

    Seminorms must satisfy:
    1. Non-negativity: ||x|| ≥ 0 for all x
    2. Triangle inequality: ||x + y|| ≤ ||x|| + ||y|| for all x, y
    3. Scalar homogeneity: ||αx|| = |α|·||x|| for all x and scalar α

    Unlike norms, seminorms do not require:
    - Definiteness: ||x|| = 0 implies x = 0
    """

    @abstractmethod
    def compute(self, x: InputType) -> float:
        """
        Compute the seminorm of the input.

        Parameters
        ----------
        x : InputType
            The input to compute the seminorm for. Can be a vector, matrix,
            sequence, string, or callable.

        Returns
        -------
        float
            The seminorm value (non-negative real number)

        Raises
        ------
        TypeError
            If the input type is not supported
        ValueError
            If the computation cannot be performed on the given input
        """
        pass

    @abstractmethod
    def check_triangle_inequality(self, x: InputType, y: InputType) -> bool:
        """
        Check if the triangle inequality property holds for the given inputs.

        The triangle inequality states that:
        ||x + y|| ≤ ||x|| + ||y||

        Parameters
        ----------
        x : InputType
            First input to check
        y : InputType
            Second input to check

        Returns
        -------
        bool
            True if the triangle inequality holds, False otherwise

        Raises
        ------
        TypeError
            If the input types are not supported or compatible
        ValueError
            If the check cannot be performed on the given inputs
        """
        pass

    @abstractmethod
    def check_scalar_homogeneity(self, x: InputType, alpha: T) -> bool:
        """
        Check if the scalar homogeneity property holds for the given input and scalar.

        The scalar homogeneity states that:
        ||αx|| = |α|·||x||

        Parameters
        ----------
        x : InputType
            The input to check
        alpha : T
            The scalar to multiply by

        Returns
        -------
        bool
            True if scalar homogeneity holds, False otherwise

        Raises
        ------
        TypeError
            If the input type is not supported
        ValueError
            If the check cannot be performed on the given input
        """
        pass
