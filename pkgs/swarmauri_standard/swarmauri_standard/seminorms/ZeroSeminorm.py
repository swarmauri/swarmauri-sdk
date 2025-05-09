import logging
from abc import ABC
from typing import TypeVar, Union, Sequence, Callable, Literal

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.seminorms.ISeminorm import ISeminorm

logger = logging.getLogger(__name__)

T = TypeVar('T', Union[Sequence, str, Callable])

@ComponentBase.register_type(SeminormBase, "ZeroSeminorm")
class ZeroSeminorm(SeminormBase):
    """
    A trivial seminorm that assigns zero to all inputs.

    This is a degenerate seminorm implementation that does not separate points,
    as every input is mapped to zero. It satisfies the seminorm properties
    trivially but provides no meaningful distinction between different inputs.

    Attributes:
        resource: The resource type identifier for this component.
    """
    
    resource: str = ResourceTypes.SEMINORM.value
    type: Literal["ZeroSeminorm"] = "ZeroSeminorm"
    
    def compute(self, input: T) -> float:
        """
        Computes the seminorm value for the given input.

        Since this is a trivial seminorm, the result is always zero regardless
        of the input.

        Args:
            input: The input to compute the seminorm for. The type can be a
                vector, matrix, sequence, string, or callable.

        Returns:
            float: The computed seminorm value, which is always 0.0.

        Examples:
            >>> seminorm.compute("any_input")
            0.0
        """
        logger.debug("Computing ZeroSeminorm value")
        return 0.0
    
    def check_triangle_inequality(self, a: T, b: T) -> bool:
        """
        Checks if the triangle inequality holds for the given inputs.

        For the ZeroSeminorm, this property trivially holds because:
        seminorm(a + b) = 0 ≤ 0 + 0 = seminorm(a) + seminorm(b)

        Args:
            a: The first input
            b: The second input

        Returns:
            bool: True, as the triangle inequality holds
        """
        logger.debug("Checking triangle inequality")
        return True
    
    def check_scalar_homogeneity(self, a: T, scalar: float) -> bool:
        """
        Checks if the scalar homogeneity property holds.

        For the ZeroSeminorm, this property trivially holds because:
        seminorm(c * a) = 0 = |c| * 0 = |c| * seminorm(a)

        Args:
            a: The input to check
            scalar: The scalar to test homogeneity with

        Returns:
            bool: True, as scalar homogeneity holds
        """
        logger.debug("Checking scalar homogeneity")
        return True