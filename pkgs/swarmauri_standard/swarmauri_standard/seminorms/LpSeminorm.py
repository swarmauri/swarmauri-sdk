from typing import Union, Sequence, Optional, Literal
from abc import ABC
from swarmauri_core.seminorms.ISeminorm import ISeminorm
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SeminormBase, "LpSeminorm")
class LpSeminorm(SeminormBase):
    """
    A concrete implementation of a non-point-separating Lp seminorm.

    This class provides the implementation for computing the Lp seminorm,
    which is a non-point-separating variant of the standard Lp norm. It
    inherits from the SeminormBase class and implements the required methods
    for computing the seminorm and checking its properties.

    The Lp seminorm is defined as the sum of the absolute values of the
    vector elements each raised to the power of p, then taking the p-th root.
    The parameter p must be in the range (0, ∞).

    Attributes:
        p (float): The parameter controlling the norm's sensitivity to
            large values. Must be in the range (0, ∞).
    """
    type: Literal["LpSeminorm"] = "LpSeminorm"

    def __init__(self, p: float = 2.0) -> None:
        """
        Initialize the LpSeminorm instance.

        Args:
            p (float): The parameter for the Lp seminorm. Must be in (0, ∞).
                Defaults to 2.0.

        Raises:
            ValueError: If p is not in the range (0, ∞).
        """
        super().__init__()
        if p <= 0:
            raise ValueError("p must be in the range (0, ∞)")
        self.p = p

    def compute(
        self,
        input: Union[IVector, IMatrix, Sequence, str, Callable]
    ) -> float:
        """
        Compute the Lp seminorm of the given input.

        Args:
            input: The input to compute the seminorm for. Can be a vector,
                matrix, sequence, string, or callable object.

        Returns:
            float: The computed seminorm value.

        Raises:
            TypeError: If the input type is not supported.
        """
        logger.debug("Computing Lp seminorm")
        
        # Convert input to a vector if it's a sequence
        if isinstance(input, Sequence) and not isinstance(input, (IVector, IMatrix, str, Callable)):
            input = IVector(input)
            
        # Handle different input types
        if isinstance(input, IVector):
            vector = input
            elements = vector.get_component()
        elif isinstance(input, IMatrix):
            vector = input
            elements = vector.get_rows()
        else:
            raise TypeError("Unsupported input type for LpSeminorm.compute")
        
        # Compute the Lp seminorm
        sum_power = sum(abs(e)**self.p for e in elements)
        return sum_power ** (1.0 / self.p)

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
        """
        logger.debug("Checking triangle inequality for LpSeminorm")
        
        seminorm_a = self.compute(a)
        seminorm_b = self.compute(b)
        seminorm_sum = self.compute(a + b)
        
        return seminorm_sum <= (seminorm_a + seminorm_b)

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
        """
        logger.debug("Checking scalar homogeneity for LpSeminorm")
        
        scaled_input = scalar * input
        seminorm_scaled = self.compute(scaled_input)
        seminorm_original = self.compute(input)
        
        return seminorm_scaled == abs(scalar) * seminorm_original