from typing import TypeVar, Union, Sequence, Literal
import logging
import math
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.norms.NormBase import NormBase

T = TypeVar("T", Sequence[float], Union[float, Sequence[float]])


@ComponentBase.register_type(NormBase, "GeneralLpNorm")
class GeneralLpNorm(NormBase):
    """
    A concrete implementation of the Lp norm for various values of p > 1.

    This class provides functionality to compute the Lp norm of vectors. The Lp norm
    is defined as the nth root of the sum of the absolute values of the vector elements
    each raised to the power p.

    Attributes:
        p: The parameter of the Lp norm. Must be finite and greater than 1.
    """

    type: Literal["GeneralLpNorm"] = "GeneralLpNorm"
    p: float

    def __init__(self, p: float = 2.0):
        """
        Initializes the GeneralLpNorm instance with specified p value.

        Args:
            p: The parameter of the Lp norm. Must be finite and greater than 1.

        Raises:
            ValueError: If p is not finite or p <= 1.
        """
        super().__init__()
        if not (math.isfinite(p) and p > 1):
            raise ValueError(f"p must be finite and greater than 1, got {p}")
        self.p = p

    def compute(self, x: T) -> float:
        """
        Computes the Lp norm of the input vector.

        Args:
            x: Input vector or sequence of numbers.

        Returns:
            float: Computed Lp norm value.

        Raises:
            ValueError: If input is invalid or cannot be processed.
        """
        logger.debug(f"Computing L{self.p} norm for input: {x}")
        if not isinstance(x, Sequence):
            raise ValueError("Input must be a sequence of numbers")

        sum_values = sum(abs(e) ** self.p for e in x)
        return math.pow(sum_values, 1.0 / self.p)

    def __repr__(self) -> str:
        """
        Returns a string representation of the GeneralLpNorm instance.

        Returns:
            str: String representation showing the class name and p value.
        """
        return f"GeneralLpNorm(p={self.p})"


logger = logging.getLogger(__name__)
