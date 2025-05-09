from typing import Union, Sequence, Callable, Optional
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.norms.INorm import INorm
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class NormBase(INorm, ComponentBase):
    """
    Base implementation for norm computations. This class provides a foundation
    for implementing different types of norms by defining the interface and
    base functionality while leaving specific implementations to subclasses.

    Inherits From:
        INorm: Interface defining the norm computation contract
        ComponentBase: Base class for all components in the system

    Attributes:
        resource: Type of resource this component represents
    """
    resource: Optional[str] = Field(default=ResourceTypes.NORM.value)

    def compute(self, x: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Compute the norm of the input.

        Args:
            x: The input to compute the norm of. Can be a vector, matrix, sequence,
                string, or callable.

        Returns:
            float: The computed norm value.

        Raises:
            NotImplementedError: This method must be implemented in a subclass.
        """
        logger.error("compute() not implemented in NormBase")
        raise NotImplementedError("compute() must be implemented in a subclass")

    def check_non_negativity(self, x: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Verify the non-negativity property of the norm.

        The norm must satisfy ||x|| >= 0 for all x, and ||x|| = 0 if and only if x = 0.

        Args:
            x: The input to verify non-negativity for.

        Raises:
            NotImplementedError: This method must be implemented in a subclass.
        """
        logger.error("check_non_negativity() not implemented in NormBase")
        raise NotImplementedError("check_non_negativity() must be implemented in a subclass")

    def check_triangle_inequality(self, x: Union[IVector, IMatrix, Sequence, str, Callable],
                                    y: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Verify the triangle inequality property of the norm.

        The norm must satisfy ||x + y|| <= ||x|| + ||y|| for all x, y.

        Args:
            x: The first input vector.
            y: The second input vector.

        Raises:
            NotImplementedError: This method must be implemented in a subclass.
        """
        logger.error("check_triangle_inequality() not implemented in NormBase")
        raise NotImplementedError("check_triangle_inequality() must be implemented in a subclass")

    def check_absolute_homogeneity(self, x: Union[IVector, IMatrix, Sequence, str, Callable],
                                    alpha: float) -> None:
        """
        Verify the absolute homogeneity property of the norm.

        The norm must satisfy ||αx|| = |α| ||x|| for all scalars α and vectors x.

        Args:
            x: The input vector.
            alpha: The scalar to scale the vector by.

        Raises:
            NotImplementedError: This method must be implemented in a subclass.
        """
        logger.error("check_absolute_homogeneity() not implemented in NormBase")
        raise NotImplementedError("check_absolute_homogeneity() must be implemented in a subclass")

    def check_definiteness(self, x: Union[IVector, IMatrix, Sequence, str, Callable]) -> None:
        """
        Verify the definiteness property of the norm.

        The norm must satisfy ||x|| = 0 if and only if x = 0.

        Args:
            x: The input to verify definiteness for.

        Raises:
            NotImplementedError: This method must be implemented in a subclass.
        """
        logger.error("check_definiteness() not implemented in NormBase")
        raise NotImplementedError("check_definiteness() must be implemented in a subclass")