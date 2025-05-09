import logging
from dataclasses import Field
from typing import Optional, Sequence, TypeVar

from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.norms.INorm import INorm
from swarmauri_core.vectors.IVector import IVector

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

# Define a TypeVar to represent supported input types
T = TypeVar("T", IVector, IMatrix, str, callable, Sequence[float])


@ComponentBase.register_model()
class NormBase(INorm, ComponentBase):
    """
    A base class implementing INorm interface providing template logic for norm behaviors.

    This class provides a basic structure for norm computations. It implements all
    abstract methods from INorm with base implementations that raise NotImplementedError,
    requiring subclasses to provide concrete implementations.

    Attributes:
        resource: Type of resource this class represents.

    Methods:
        compute: Abstract method to compute the norm of input.
        check_non_negativity: Verifies non-negativity property.
        check_triangle_inequality: Verifies triangle inequality property.
        check_absolute_homogeneity: Verifies absolute homogeneity property.
        check_definiteness: Verifies definiteness property.
    """

    resource: Optional[str] = Field(default=ResourceTypes.NORM.value)

    def compute(self, x: T) -> float:
        """
        Computes the norm of the given input vector, matrix, sequence, string, or callable.

        Args:
            x: Input to compute the norm of. Can be a vector, matrix, sequence,
               string, or callable.

        Returns:
            float: Computed norm value

        Raises:
            NotImplementedError: Method must be implemented in subclass.
        """
        logger.debug(f"Computing norm for input type {type(x)}")
        raise NotImplementedError("Method compute() must be implemented in subclass")

    def check_non_negativity(self, x: T) -> bool:
        """
        Verifies the non-negativity property of the norm.

        Args:
            x: Input to check non-negativity for

        Returns:
            bool: True if norm is non-negative, False otherwise
        """
        logger.debug("Checking non-negativity property")
        norm = self.compute(x)
        return norm >= 0

    def check_triangle_inequality(self, x: T, y: T) -> bool:
        """
        Verifies the triangle inequality property of the norm.

        Args:
            x: First input vector
            y: Second input vector

        Returns:
            bool: True if triangle inequality holds, False otherwise
        """
        logger.debug("Checking triangle inequality property")
        norm_x = self.compute(x)
        norm_y = self.compute(y)
        norm_xy = self.compute(x + y)
        return norm_xy <= norm_x + norm_y

    def check_absolute_homogeneity(self, x: T, alpha: float) -> bool:
        """
        Verifies the absolute homogeneity property of the norm.

        Args:
            x: Input vector
            alpha: Scaling factor

        Returns:
            bool: True if absolute homogeneity holds, False otherwise
        """
        logger.debug(f"Checking absolute homogeneity with alpha {alpha}")
        norm_x = self.compute(x)
        norm_alpha_x = self.compute(alpha * x)
        return norm_alpha_x == abs(alpha) * norm_x

    def check_definiteness(self, x: T) -> bool:
        """
        Verifies the definiteness property of the norm.

        A norm is definite if norm(x) = 0 if and only if x = 0.

        Args:
            x: Input vector

        Returns:
            bool: True if definiteness holds, False otherwise
        """
        logger.debug("Checking definiteness property")
        norm = self.compute(x)
        if norm == 0:
            return x == 0
        return True


logger = logging.getLogger(__name__)
