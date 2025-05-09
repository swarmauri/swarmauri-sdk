import logging
from typing import Callable, Optional, Union

from pydantic import Field
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.seminorms.ISeminorm import ISeminorm
from swarmauri_core.vectors.IVector import IVector

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class SeminormBase(ISeminorm, ComponentBase):
    """
    Base class providing tools for evaluating seminorms in partial vector spaces.

    This class serves as a reusable implementation for defining seminorm structures.
    It implements the core interface defined by ISeminorm and provides basic functionality
    that can be extended by specific seminorm implementations.

    Attributes:
        resource: Optional[str] - The resource type identifier for this component

    Methods:
        compute: Abstract method for computing the seminorm value
        check_triangle_inequality: Verifies the triangle inequality property
        check_scalar_homogeneity: Verifies the scalar homogeneity property
        _is_vector: Helper method to check if input is an IVector instance
        _is_matrix: Helper method to check if input is an IMatrix instance
        _is_sequence: Helper method to check if input is a sequence
        _is_callable: Helper method to check if input is callable
    """

    resource: Optional[str] = Field(default=ResourceTypes.SEMINORM.value)

    def __init__(self):
        """
        Initializes the SeminormBase instance.
        """
        super().__init__()
        logger.debug("Initialized SeminormBase")

    def compute(
        self, input: Union[IVector, IMatrix, str, Callable, list, tuple]
    ) -> float:
        """
        Computes the seminorm value of the input.

        Args:
            input: The input to compute the seminorm for. Supported types are:
                - IVector: High-dimensional vector
                - IMatrix: Matrix structure
                - str: String input
                - Callable: Callable function
                - list: List of elements
                - tuple: Tuple of elements

        Returns:
            float: The computed seminorm value

        Raises:
            NotImplementedError: Method not implemented by the base class
            TypeError: If input type is not supported
        """
        logger.debug(f"Computing seminorm for input of type {type(input).__name__}")
        raise NotImplementedError("Method not implemented")

    def check_triangle_inequality(
        self,
        a: Union[IVector, IMatrix, str, Callable, list, tuple],
        b: Union[IVector, IMatrix, str, Callable, list, tuple],
    ) -> bool:
        """
        Verifies the triangle inequality property: seminorm(a + b) <= seminorm(a) + seminorm(b).

        Args:
            a: First element to check
            b: Second element to check

        Returns:
            bool: True if triangle inequality holds, False otherwise
        """
        logger.debug("Checking triangle inequality")
        raise NotImplementedError("Method not implemented")

    def check_scalar_homogeneity(
        self,
        a: Union[IVector, IMatrix, str, Callable, list, tuple],
        scalar: Union[int, float],
    ) -> bool:
        """
        Verifies the scalar homogeneity property: seminorm(s * a) = |s| * seminorm(a).

        Args:
            a: Element to check
            scalar: Scalar value to scale with

        Returns:
            bool: True if scalar homogeneity holds, False otherwise
        """
        logger.debug(f"Checking scalar homogeneity with scalar {scalar}")
        raise NotImplementedError("Method not implemented")

    def _is_vector(
        self, input: Union[IVector, IMatrix, str, Callable, list, tuple]
    ) -> bool:
        """
        Helper method to check if input is an IVector instance.

        Args:
            input: Input to check

        Returns:
            bool: True if input is an IVector, False otherwise
        """
        return isinstance(input, IVector)

    def _is_matrix(
        self, input: Union[IVector, IMatrix, str, Callable, list, tuple]
    ) -> bool:
        """
        Helper method to check if input is an IMatrix instance.

        Args:
            input: Input to check

        Returns:
            bool: True if input is an IMatrix, False otherwise
        """
        return isinstance(input, IMatrix)

    def _is_sequence(
        self, input: Union[IVector, IMatrix, str, Callable, list, tuple]
    ) -> bool:
        """
        Helper method to check if input is a sequence (list or tuple).

        Args:
            input: Input to check

        Returns:
            bool: True if input is a sequence, False otherwise
        """
        return isinstance(input, (list, tuple))

    def _is_callable(
        self, input: Union[IVector, IMatrix, str, Callable, list, tuple]
    ) -> bool:
        """
        Helper method to check if input is a callable function.

        Args:
            input: Input to check

        Returns:
            bool: True if input is callable, False otherwise
        """
        return isinstance(input, Callable)

    def __str__(self) -> str:
        """
        Returns a string representation of the seminorm instance.

        Returns:
            str: String representation
        """
        return "SeminormBase()"

    def __repr__(self) -> str:
        """
        Returns the official string representation of the seminorm instance.

        Returns:
            str: Official string representation
        """
        return self.__str__()
