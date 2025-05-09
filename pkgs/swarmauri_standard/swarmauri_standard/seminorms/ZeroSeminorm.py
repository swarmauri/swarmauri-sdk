from swarmauri_base.seminorms import SeminormBase
from typing import Union, Sequence, Callable
from abc import ABC
import logging

logger = logging.getLogger(__name__)


@SeminormBase.register_type(SeminormBase, "ZeroSeminorm")
class ZeroSeminorm(SeminormBase):
    """
    A trivial seminorm that assigns zero to all inputs.

    This class implements a degenerate seminorm where every input is mapped
    to zero. It does not satisfy the separation property of seminorms since
    all inputs are treated equally regardless of their characteristics.
    """

    type: str = "ZeroSeminorm"

    def compute(self, input: Union[Sequence, Callable, str]) -> float:
        """
        Compute the seminorm of the given input.

        Since this is a zero seminorm, the result will always be 0.0
        regardless of the input provided.

        Args:
            input: The input to compute the seminorm for. Can be a vector,
                matrix, sequence, string, or callable object.

        Returns:
            float: The computed seminorm value, which is always 0.0.
        """
        logger.debug("Computing zero seminorm for input")
        return 0.0

    def check_triangle_inequality(
        self, a: Union[Sequence, Callable, str], b: Union[Sequence, Callable, str]
    ) -> bool:
        """
        Check if the triangle inequality holds.

        For the zero seminorm, this will always return True since:
        seminorm(a + b) = 0 <= 0 + 0 = seminorm(a) + seminorm(b)

        Args:
            a: The first element to check
            b: The second element to check

        Returns:
            bool: True, as the triangle inequality holds trivially
        """
        logger.debug("Checking triangle inequality for zero seminorm")
        return True

    def check_scalar_homogeneity(
        self, input: Union[Sequence, Callable, str], scalar: float
    ) -> bool:
        """
        Check if the seminorm satisfies scalar homogeneity.

        For the zero seminorm, this will always return True since:
        seminorm(c * input) = 0 = |c| * 0 = |c| * seminorm(input)

        Args:
            input: The input element to check
            scalar: The scalar to scale the input by

        Returns:
            bool: True, as scalar homogeneity holds trivially
        """
        logger.debug("Checking scalar homogeneity for zero seminorm")
        return True
