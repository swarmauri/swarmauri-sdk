from typing import Literal, Sequence, Iterable
import logging
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.norms.NormBase import NormBase, T

logger = logging.getLogger(__name__)


@ComponentBase.register_type(NormBase, "L1ManhattanNorm")
class L1ManhattanNorm(NormBase):
    """
    A class implementing the L1 (Manhattan) norm computation for real vectors.

    This class provides the concrete implementation for computing the L1 norm,
    which is the sum of the absolute values of the vector components.

    Inherits from:
        NormBase: Base class providing template logic for norm computations.

    Attributes:
        type: Literal["L1ManhattanNorm"] = "L1ManhattanNorm"
            Type identifier for this norm class.

    Methods:
        compute: Computes the L1 norm of the input vector.
    """

    type: Literal["L1ManhattanNorm"] = "L1ManhattanNorm"

    def compute(self, x: T) -> float:
        """
        Computes the L1 (Manhattan) norm of the input vector.

        The L1 norm is calculated as the sum of the absolute values of the
        vector components. This implementation handles various input types
        including lists, tuples, and strings by treating them as sequences of
        numerical values.

        Args:
            x: Input vector or sequence of numerical values.

        Returns:
            float: The computed L1 norm value.

        Raises:
            TypeError: If the input type is not supported.
        """
        logger.debug("Computing L1 Manhattan norm")

        # Check if input is a valid numerical sequence
        if not isinstance(x, (Iterable, Sequence)):
            raise TypeError("Input must be an iterable or sequence type")

        try:
            # Convert input to list and compute sum of absolute values
            vector = list(x)
            absolute_sum = sum(abs(float(component)) for component in vector)
            logger.debug(f"L1 norm computed as {absolute_sum}")
            return float(absolute_sum)
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to compute L1 norm: {str(e)}")
            raise TypeError(f"Invalid input type for L1 norm computation: {str(e)}")
