from typing import TypeVar, Union, Callable, Sequence, Optional
import logging
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.norms.INorm import INorm
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

# Configure logging
logger = logging.getLogger(__name__)

# Define type variables for supported input types
T = TypeVar("T")
VectorType = TypeVar("VectorType", bound=IVector)
MatrixType = TypeVar("MatrixType", bound=IMatrix)
SequenceType = TypeVar("SequenceType", bound=Sequence)
StringType = TypeVar("StringType", bound=str)
CallableType = TypeVar("CallableType", bound=Callable)


@ComponentBase.register_model()
class NormBase(INorm, ComponentBase):
    """
    Base class for norm computations on vector spaces.

    This class provides a template implementation for norm behaviors,
    implementing common normalization patterns across vector norms.

    Attributes
    ----------
    resource : str, optional
        The resource type, defaults to NORM.
    """

    resource: Optional[str] = Field(default=ResourceTypes.NORM.value)

    def compute(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> float:
        """
        Compute the norm of the input.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input for which to compute the norm.

        Returns
        -------
        float
            The computed norm value.

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        TypeError
            If the input type is not supported.
        ValueError
            If the norm cannot be computed for the given input.
        """
        raise NotImplementedError(
            "The compute method must be implemented by subclasses."
        )

    def check_non_negativity(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> bool:
        """
        Check if the norm satisfies the non-negativity property.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input to check.

        Returns
        -------
        bool
            True if the norm is non-negative, False otherwise.

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        raise NotImplementedError(
            "The check_non_negativity method must be implemented by subclasses."
        )

    def check_definiteness(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> bool:
        """
        Check if the norm satisfies the definiteness property.

        The definiteness property states that the norm of x is 0 if and only if x is 0.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input to check.

        Returns
        -------
        bool
            True if the norm satisfies the definiteness property, False otherwise.

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        raise NotImplementedError(
            "The check_definiteness method must be implemented by subclasses."
        )

    def check_triangle_inequality(
        self,
        x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType],
        y: Union[VectorType, MatrixType, SequenceType, StringType, CallableType],
    ) -> bool:
        """
        Check if the norm satisfies the triangle inequality.

        The triangle inequality states that norm(x + y) <= norm(x) + norm(y).

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The first input.
        y : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The second input.

        Returns
        -------
        bool
            True if the norm satisfies the triangle inequality, False otherwise.

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        TypeError
            If the inputs are not of the same type or cannot be added.
        """
        raise NotImplementedError(
            "The check_triangle_inequality method must be implemented by subclasses."
        )

    def check_absolute_homogeneity(
        self,
        x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType],
        scalar: float,
    ) -> bool:
        """
        Check if the norm satisfies the absolute homogeneity property.

        The absolute homogeneity property states that norm(a*x) = |a|*norm(x) for scalar a.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input.
        scalar : float
            The scalar value.

        Returns
        -------
        bool
            True if the norm satisfies the absolute homogeneity property, False otherwise.

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        TypeError
            If the input cannot be scaled by the scalar.
        """
        raise NotImplementedError(
            "The check_absolute_homogeneity method must be implemented by subclasses."
        )
