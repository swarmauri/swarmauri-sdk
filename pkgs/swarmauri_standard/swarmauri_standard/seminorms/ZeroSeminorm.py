from typing import TypeVar, Union
import logging
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.seminorms.ISeminorm import ISeminorm

# Configure logging
logger = logging.getLogger(__name__)

# Define type variable for input types
T = TypeVar('T', Union[str, callable, Sequence[float], Sequence[Sequence[float]]])

@ComponentBase.register_type(SeminormBase, "ZeroSeminorm")
class ZeroSeminorm(SeminormBase):
    """
    A trivial seminorm implementation that assigns zero to all inputs.

    This class implements a degenerate seminorm that does not separate points. It
    serves as a simple example of a seminorm implementation and can be used as
    a placeholder or for testing purposes.

    Attributes:
        resource: str = ResourceTypes.SEMINORM.value
            The resource type identifier for this component.
    """
    resource: str = ResourceTypes.SEMINORM.value
    
    def __init__(self):
        """
        Initialize the ZeroSeminorm instance.
        
        Initializes the base class and sets up the component.
        """
        super().__init__()
        
    def compute(self, input: T) -> float:
        """
        Compute the seminorm of the given input.

        Since this is a trivial implementation, the seminorm value will always
        be 0 regardless of the input.

        Args:
            input: T
                The input to compute the seminorm on. This can be a vector, matrix,
                sequence, string, or callable.

        Returns:
            float:
                The computed seminorm value, which will always be 0.0.
        """
        logger.debug("Computing zero seminorm for input of type {}".format(type(input)))
        return 0.0

    def check_triangle_inequality(self, a: T, b: T) -> bool:
        """
        Check if the triangle inequality holds for the given inputs.

        For this trivial seminorm, since both seminorm(a) and seminorm(b)
        will be 0, the inequality 0 <= 0 + 0 holds true.

        Args:
            a: T
                The first input.
            b: T
                The second input.

        Returns:
            bool:
                True, since 0 <= 0 + 0 is always true.
        """
        logger.debug("Checking triangle inequality for zero seminorm")
        return True

    def check_scalar_homogeneity(self, a: T, scalar: float) -> bool:
        """
        Check if scalar homogeneity holds for the given input and scalar.

        For this trivial seminorm, since seminorm(c * a) will be 0 and
        c * seminorm(a) will also be 0, the equality holds.

        Args:
            a: T
                The input to check.
            scalar: float
                The scalar to check against.

        Returns:
            bool:
                True, since 0 = 0 * c for any scalar c.
        """
        logger.debug("Checking scalar homogeneity for zero seminorm")
        return True