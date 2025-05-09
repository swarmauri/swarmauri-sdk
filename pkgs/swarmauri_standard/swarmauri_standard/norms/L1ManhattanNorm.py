import logging
from typing import Union, Any
from swarmauri_base.norms.NormBase import NormBase
from swarmauri_core.vectors.IVector import IVector

logger = logging.getLogger(__name__)

class L1ManhattanNorm(NormBase):
    """Concrete implementation of the L1 (Manhattan) norm for real vectors.

    This class computes the L1 norm (sum of absolute values) for vectors.
    It inherits from the NormBase class and implements the required compute method.
    """

    type: str = "L1ManhattanNorm"

    def __init__(self):
        """Initialize the L1ManhattanNorm instance."""
        super().__init__()
        self._type = self.type

    def compute(self, x: Union[IVector, Any]) -> float:
        """Compute the L1 (Manhattan) norm of the input vector.

        Args:
            x: The input vector. Can be an IVector instance or any sequence type.

        Returns:
            float: The L1 norm value of the input vector.

        Raises:
            ValueError: If the input type is not supported.
        """
        logger.debug("Starting L1 norm computation")
        
        if isinstance(x, IVector):
            vector = x.data
        elif isinstance(x, (list, tuple, Sequence)):
            vector = x
        elif callable(x):
            vector = x()
        else:
            raise ValueError(f"Unsupported input type: {type(x)}")
        
        # Compute sum of absolute values of vector components
        norm_value = sum(abs(component) for component in vector)
        
        logger.debug(f"L1 norm computed successfully: {norm_value}")
        return norm_value

    def __str__(self) -> str:
        """Return string representation of the L1ManhattanNorm instance."""
        return f"L1ManhattanNorm()"

    def __repr__(self) -> str:
        """Return official string representation of the L1ManhattanNorm instance."""
        return f"L1ManhattanNorm()"