from typing import TypeVar, Union
import logging
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.seminorms.ISeminorm import ISeminorm

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T', Union[IVector, IMatrix, str, callable, Sequence[float], Sequence[Sequence[float]]])

@ComponentBase.register_model()
class SeminormBase(ISeminorm, ComponentBase):
    """
    Base class providing common functionality for seminorm implementations.

    This class implements the core interface defined by ISeminorm and provides
    basic structure and logging capabilities for all seminorm implementations.
    Concrete implementations should extend this class and provide specific
    implementations for the abstract methods.

    Attributes:
        resource: Optional[str] = ResourceTypes.SEMINORM.value
            The resource type identifier for this component.
    """
    resource: str = ResourceTypes.SEMINORM.value
    
    def compute(self, input: T) -> float:
        """
        Compute the seminorm of the given input.

        Args:
            input: T
                The input to compute the seminorm on. This can be a vector, matrix,
                sequence, string, or callable.

        Returns:
            float:
                The computed seminorm value.

        Raises:
            NotImplementedError:
                This method must be implemented in a concrete subclass.
        """
        logger.error("compute() called on base class - must be implemented in subclass")
        raise NotImplementedError("compute() must be implemented in a concrete subclass")

    def check_triangle_inequality(self, a: T, b: T) -> bool:
        """
        Check if the triangle inequality holds for the given inputs.

        The triangle inequality states that for any two vectors a and b:
        seminorm(a + b) <= seminorm(a) + seminorm(b)

        Args:
            a: T
                The first input.
            b: T
                The second input.

        Returns:
            bool:
                True if the triangle inequality holds, False otherwise.

        Raises:
            NotImplementedError:
                This method must be implemented in a concrete subclass.
        """
        logger.error("check_triangle_inequality() called on base class - must be implemented in subclass")
        raise NotImplementedError("check_triangle_inequality() must be implemented in a concrete subclass")

    def check_scalar_homogeneity(self, a: T, scalar: float) -> bool:
        """
        Check if scalar homogeneity holds for the given input and scalar.

        Scalar homogeneity states that for any vector a and scalar c >= 0:
        seminorm(c * a) = c * seminorm(a)

        Args:
            a: T
                The input to check.
            scalar: float
                The scalar to check against.

        Returns:
            bool:
                True if scalar homogeneity holds, False otherwise.

        Raises:
            NotImplementedError:
                This method must be implemented in a concrete subclass.
        """
        logger.error("check_scalar_homogeneity() called on base class - must be implemented in subclass")
        raise NotImplementedError("check_scalar_homogeneity() must be implemented in a concrete subclass")