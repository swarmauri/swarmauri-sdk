from typing import Literal
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.norms.base.NormBase import NormBase

class ManhattanNorm(NormBase):
    """
    Discrete Manhattan norm (Manhattan norm) implementation.

    The Discrete Manhattan norm is the sum of the absolute values of the vector elements.
    """
    type: Literal['ManhattanNorm'] = "ManhattanNorm"

    def compute(self, x: Vector) -> float:
        """
        Compute the Discrete Manhattan norm of a vector.

        Args:
            x: The vector whose Discrete Manhattan norm is to be computed.

        Returns:
            A float representing the Discrete Manhattan norm.
        """
        # Compute the Discrete Manhattan norm as the sum of absolute values
        return sum(abs(value) for value in x.value)
