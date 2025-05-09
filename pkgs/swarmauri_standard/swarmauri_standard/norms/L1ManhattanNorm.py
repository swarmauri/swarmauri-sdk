from typing import Union, TypeVar, Optional
import logging
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.norms.NormBase import NormBase
from swarmauri_core.norms.INorm import INorm

T = TypeVar('T', Union['IVector', 'IMatrix', str, bytes, Sequence, Callable])

@ComponentBase.register_model()
class L1ManhattanNorm(NormBase):
    """
    Concrete implementation of the L1 (Manhattan) norm for real vectors.
    
    Inherits From:
        NormBase: Base class providing template logic for norm computations.
        INorm: Interface for norm computations on vector spaces.
        ComponentBase: Base class for all components in the system.
    
    Provides:
        Implementation of L1 norm computation and associated properties.
    """
    resource: Optional[str] = Field(default=ResourceTypes.NORM.value)
    type: Literal["L1ManhattanNorm"] = "L1ManhattanNorm"
    
    def __init__(self):
        """
        Initializes the L1ManhattanNorm instance.
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.debug("L1ManhattanNorm instance initialized")

    def compute(self, x: T) -> float:
        """
        Computes the L1 (Manhattan) norm of a vector.
        
        Args:
            x: T
                The input vector for which to compute the norm.
                Expected to be an iterable of numerical values.
                
        Returns:
            float:
                The computed L1 norm value.
                
        Raises:
            ValueError: If the input is not a valid vector type.
        """
        self.logger.debug("Computing L1 norm")
        try:
            # Convert to list of absolute values and sum them
            return float(sum(abs(component) for component in x))
        except TypeError:
            raise ValueError("Input must be an iterable of numerical values")

    def check_non_negativity(self, x: T) -> bool:
        """
        Checks if the L1 norm satisfies non-negativity.
        
        Args:
            x: T
                The input vector to check.
                
        Returns:
            bool:
                True if norm(x) >= 0, False otherwise.
        """
        self.logger.debug("Checking non-negativity for L1 norm")
        # L1 norm is always non-negative since it's sum of absolute values
        return self.compute(x) >= 0

    def check_triangle_inequality(self, x: T, y: T) -> bool:
        """
        Checks if the L1 norm satisfies the triangle inequality.
        
        Args:
            x: T
                The first input vector
            y: T
                The second input vector
                
        Returns:
            bool:
                True if ||x + y|| <= ||x|| + ||y||, False otherwise.
        """
        self.logger.debug("Checking triangle inequality for L1 norm")
        norm_x = self.compute(x)
        norm_y = self.compute(y)
        norm_xy = self.compute([x[i] + y[i] for i in range(len(x))])
        return norm_xy <= norm_x + norm_y

    def check_absolute_homogeneity(self, x: T, scalar: float) -> bool:
        """
        Checks if the L1 norm satisfies absolute homogeneity.
        
        Args:
            x: T
                The input vector to check
            scalar: float
                The scalar to scale with
                
        Returns:
            bool:
                True if ||c * x|| = |c| * ||x||, False otherwise.
        """
        self.logger.debug("Checking absolute homogeneity for L1 norm")
        scaled_norm = self.compute([scalar * component for component in x])
        expected_norm = abs(scalar) * self.compute(x)
        return scaled_norm == expected_norm

    def check_definiteness(self, x: T) -> bool:
        """
        Checks if the L1 norm is definite (norm(x) = 0 if and only if x = 0).
        
        Args:
            x: T
                The input vector to check
                
        Returns:
            bool:
                True if norm(x) = 0 implies x = 0, False otherwise.
        """
        self.logger.debug("Checking definiteness for L1 norm")
        norm = self.compute(x)
        # Check if norm is zero and vector is zero vector
        return norm == 0 and all(component == 0 for component in x)