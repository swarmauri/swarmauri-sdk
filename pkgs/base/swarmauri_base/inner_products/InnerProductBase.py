"""Module implementing the IInnerProduct interface for swarmauri_core package."""

from abc import ABC, abstractmethod
import logging

# Set up logger
logger = logging.getLogger(__name__)


class IInnerProduct(ABC):
    """
    Interface defining the contract for inner product operations.

    This abstract base class provides the interface for computing inner products
    and checking their mathematical properties.

    Methods:
        compute(a, b): Computes the inner product of vectors a and b.
        check_conjugate_symmetry(a, b): Checks if the inner product is conjugate symmetric.
        check_linearity(a, b, c): Checks if the inner product is linear in the first argument.
        check_positivity(a): Checks if the inner product is positive definite.
    """

    @abstractmethod
    def compute(self, a: object, b: object) -> float:
        """
        Computes the inner product of two vectors, matrices, or callables.

        Args:
            a: The first vector, matrix, or callable.
            b: The second vector, matrix, or callable.

        Returns:
            A float representing the inner product result.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        logger.error("compute method not implemented in subclass")
        raise NotImplementedError("compute method must be implemented in a subclass")

    @abstractmethod
    def check_conjugate_symmetry(self, a: object, b: object) -> bool:
        """
        Checks if the inner product is conjugate symmetric, i.e., <a, b> = <b, a>*.

        Args:
            a: The first vector or matrix.
            b: The second vector or matrix.

        Returns:
            bool: True if the inner product is conjugate symmetric, False otherwise.
        """
        logger.error("check_conjugate_symmetry method not implemented in subclass")
        raise NotImplementedError("check_conjugate_symmetry method must be implemented in a subclass")

    @abstractmethod
    def check_linearity(self, a: object, b: object, c: object) -> bool:
        """
        Checks if the inner product is linear in the first argument.

        Args:
            a: The first vector or matrix.
            b: The second vector or matrix.
            c: A scalar for linearity check.

        Returns:
            bool: True if the inner product is linear, False otherwise.
        """
        logger.error("check_linearity method not implemented in subclass")
        raise NotImplementedError("check_linearity method must be implemented in a subclass")

    @abstractmethod
    def check_positivity(self, a: object) -> bool:
        """
        Checks if the inner product is positive definite.

        Args:
            a: The vector or matrix to check.

        Returns:
            bool: True if the inner product is positive definite, False otherwise.
        """
        logger.error("check_positivity method not implemented in subclass")
        raise NotImplementedError("check_positivity method must be implemented in a subclass")