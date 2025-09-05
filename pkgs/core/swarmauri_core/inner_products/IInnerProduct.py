import logging
from abc import ABC, abstractmethod
from typing import Callable, TypeVar, Union

import numpy as np

from swarmauri_core.vectors.IVector import IVector

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar("T")
Vector = TypeVar("Vector", bound="IVector")
Matrix = TypeVar("Matrix", bound=np.ndarray)


class IInnerProduct(ABC):
    """
    Interface defining the contract for inner product operations.

    This interface requires implementation of methods to compute inner products
    between vectors, matrices, or callables, as well as methods to verify
    mathematical properties of the inner product such as conjugate symmetry,
    linearity, and positivity.
    """

    @abstractmethod
    def compute(
        self, a: Union[Vector, Matrix, Callable], b: Union[Vector, Matrix, Callable]
    ) -> float:
        """
        Compute the inner product between two objects.

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The first object for inner product calculation
        b : Union[Vector, Matrix, Callable]
            The second object for inner product calculation

        Returns
        -------
        float
            The inner product value
        """
        pass

    @abstractmethod
    def check_conjugate_symmetry(
        self, a: Union[Vector, Matrix, Callable], b: Union[Vector, Matrix, Callable]
    ) -> bool:
        """
        Check if the inner product satisfies the conjugate symmetry property:
        <a, b> = <b, a>* (complex conjugate).

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The first object
        b : Union[Vector, Matrix, Callable]
            The second object

        Returns
        -------
        bool
            True if conjugate symmetry holds, False otherwise
        """
        pass

    @abstractmethod
    def check_linearity_first_argument(
        self,
        a1: Union[Vector, Matrix, Callable],
        a2: Union[Vector, Matrix, Callable],
        b: Union[Vector, Matrix, Callable],
        alpha: float,
        beta: float,
    ) -> bool:
        """
        Check if the inner product satisfies linearity in the first argument:
        <alpha*a1 + beta*a2, b> = alpha*<a1, b> + beta*<a2, b>.

        Parameters
        ----------
        a1 : Union[Vector, Matrix, Callable]
            First component of the first argument
        a2 : Union[Vector, Matrix, Callable]
            Second component of the first argument
        b : Union[Vector, Matrix, Callable]
            The second object
        alpha : float
            Scalar multiplier for a1
        beta : float
            Scalar multiplier for a2

        Returns
        -------
        bool
            True if linearity in the first argument holds, False otherwise
        """
        pass

    @abstractmethod
    def check_positivity(self, a: Union[Vector, Matrix, Callable]) -> bool:
        """
        Check if the inner product satisfies the positivity property:
        <a, a> >= 0 and <a, a> = 0 iff a = 0.

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The object to check positivity for

        Returns
        -------
        bool
            True if positivity holds, False otherwise
        """
        pass
