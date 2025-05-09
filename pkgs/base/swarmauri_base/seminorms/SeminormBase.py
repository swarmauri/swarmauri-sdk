from typing import Union, Sequence, Callable, Optional
from abc import ABC
from swarmauri_core.seminorms.ISeminorm import ISeminorm
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix
import logging

logger = logging.getLogger(__name__)


class SeminormBase(ISeminorm, ABC):
    """
    Base class providing fundamental implementation for seminorm structures.
    
    This class implements the core functionality required for seminorms while
    leaving specific implementation details to be defined in subclasses.
    
    The class enforces the interface defined by ISeminorm while providing
    basic structure and logging capabilities. All methods that require
    specific implementation will raise NotImplementedError.
    """
    
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
            NotImplementedError: This method must be implemented in a subclass.
            ValueError: If the input type is not supported.
            TypeError: If the input is of incorrect type.
        """
        logger.debug("Base compute method called")
        raise NotImplementedError("The compute method must be implemented in a subclass")

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

        Raises:
            NotImplementedError: This method must be implemented in a subclass.
        """
        logger.debug("Base triangle inequality check called")
        raise NotImplementedError("The check_triangle_inequality method must be implemented in a subclass")

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

        Raises:
            NotImplementedError: This method must be implemented in a subclass.
        """
        logger.debug("Base scalar homogeneity check called")
        raise NotImplementedError("The check_scalar_homogeneity method must be implemented in a subclass")