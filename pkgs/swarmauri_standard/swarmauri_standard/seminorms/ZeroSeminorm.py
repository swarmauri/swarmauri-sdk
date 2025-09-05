import logging
from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.seminorms.SeminormBase import InputType, SeminormBase, T

# Configure logging
logger = logging.getLogger(__name__)


@ComponentBase.register_type(SeminormBase, "ZeroSeminorm")
class ZeroSeminorm(SeminormBase):
    """
    Trivial seminorm that assigns zero to all inputs.

    This class implements a degenerate seminorm that returns 0 for any input.
    While it satisfies the formal requirements of a seminorm (non-negativity,
    triangle inequality, and scalar homogeneity), it does not separate points
    and is therefore not useful for most practical applications.

    Attributes
    ----------
    type : Literal["ZeroSeminorm"]
        The type identifier for this class
    """

    type: Literal["ZeroSeminorm"] = "ZeroSeminorm"

    def compute(self, x: InputType) -> float:
        """
        Compute the seminorm of the input, which is always 0.

        Parameters
        ----------
        x : InputType
            The input to compute the seminorm for. Can be a vector, matrix,
            sequence, string, or callable.

        Returns
        -------
        float
            Always returns 0.0
        """
        logger.debug(f"Computing ZeroSeminorm for input of type {type(x)}")
        return 0.0

    def check_triangle_inequality(self, x: InputType, y: InputType) -> bool:
        """
        Check if the triangle inequality property holds for the given inputs.

        For ZeroSeminorm, the triangle inequality is always satisfied since:
        ||x + y|| = 0 ≤ ||x|| + ||y|| = 0 + 0 = 0

        Parameters
        ----------
        x : InputType
            First input to check
        y : InputType
            Second input to check

        Returns
        -------
        bool
            Always returns True as the triangle inequality is trivially satisfied
        """
        logger.debug(
            f"Checking triangle inequality for ZeroSeminorm with inputs of types {type(x)} and {type(y)}"
        )
        # Triangle inequality is always satisfied for the zero seminorm
        return True

    def check_scalar_homogeneity(self, x: InputType, alpha: T) -> bool:
        """
        Check if the scalar homogeneity property holds for the given input and scalar.

        For ZeroSeminorm, scalar homogeneity is always satisfied since:
        ||αx|| = 0 = |α|·||x|| = |α|·0 = 0

        Parameters
        ----------
        x : InputType
            The input to check
        alpha : T
            The scalar to multiply by

        Returns
        -------
        bool
            Always returns True as scalar homogeneity is trivially satisfied
        """
        logger.debug(
            f"Checking scalar homogeneity for ZeroSeminorm with input of type {type(x)} and scalar {alpha}"
        )
        # Scalar homogeneity is always satisfied for the zero seminorm
        return True

    def __str__(self) -> str:
        """
        Return a string representation of the ZeroSeminorm.

        Returns
        -------
        str
            A string describing this seminorm
        """
        return "ZeroSeminorm (trivial seminorm that returns 0 for all inputs)"

    def __repr__(self) -> str:
        """
        Return a developer string representation of the ZeroSeminorm.

        Returns
        -------
        str
            A string representation suitable for debugging
        """
        return "ZeroSeminorm()"
