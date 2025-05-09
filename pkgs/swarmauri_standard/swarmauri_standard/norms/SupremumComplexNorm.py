from typing import TypeVar, Union, Sequence, Callable, Optional
import logging
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.norms.INorm import INorm

# Define a TypeVar to represent supported input types
T = TypeVar('T', Sequence[float], Callable)

@ComponentBase.register_type(NormBase, "SupremumComplexNorm")
class SupremumComplexNorm(NormBase):
    """
    A class implementing the supremum norm for complex-valued functions.
    
    This class provides the implementation for computing the supremum (maximum)
    absolute value of complex-valued functions over a specified interval [a, b].
    
    Attributes:
        type: Identifier for the norm type
        resource: Type of resource this class represents
        
    Methods:
        compute: Computes the supremum norm of the input
    """
    type: str = "SupremumComplexNorm"
    resource: Optional[str] = "norm"
    
    def __init__(self) -> None:
        """
        Initializes the SupremumComplexNorm instance.
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def compute(self, x: T) -> float:
        """
        Computes the supremum norm of the given input.
        
        The supremum norm is defined as the maximum absolute value of the
        complex-valued function over the interval [a, b].
        
        Args:
            x: Input can be either a complex-valued function (callable) or
               a sequence of complex numbers.
            
        Returns:
            float: Maximum absolute value of the input over the interval
            
        Raises:
            ValueError: If the input type is not supported
        """
        self.logger.debug("Starting supremum norm computation")
        
        if callable(x):
            # Assuming x is a function defined over interval [a, b]
            # For this example, we'll evaluate at discrete points
            # You might want to implement a more sophisticated method
            # for evaluating the function over the interval
            a = 0.0
            b = 1.0
            num_points = 1000
            max_val = 0.0
            
            for i in range(num_points + 1):
                point = a + (b - a) * i / num_points
                value = abs(x(point))
                if value > max_val:
                    max_val = value
            
            self.logger.debug(f"Computed supremum norm: {max_val}")
            return max_val
            
        elif isinstance(x, Sequence):
            # Handle sequence of complex numbers
            max_val = max(abs(val) for val in x)
            self.logger.debug(f"Computed supremum norm for sequence: {max_val}")
            return max_val
            
        else:
            self.logger.error(f"Unsupported input type: {type(x)}")
            raise ValueError(f"Unsupported input type: {type(x)}")
            
    def check_non_negativity(self, x: T) -> bool:
        """
        Verifies the non-negativity property of the norm.
        
        Args:
            x: Input to check non-negativity for
            
        Returns:
            bool: True if norm is non-negative, False otherwise
        """
        self.logger.debug("Checking non-negativity property")
        norm = self.compute(x)
        return norm >= 0

    def check_triangle_inequality(self, x: T, y: T) -> bool:
        """
        Verifies the triangle inequality property of the norm.
        
        Args:
            x: First input vector
            y: Second input vector
            
        Returns:
            bool: True if triangle inequality holds, False otherwise
        """
        self.logger.debug("Checking triangle inequality property")
        norm_x = self.compute(x)
        norm_y = self.compute(y)
        norm_xy = self.compute(x + y)
        return norm_xy <= norm_x + norm_y

    def check_absolute_homogeneity(self, x: T, alpha: float) -> bool:
        """
        Verifies the absolute homogeneity property of the norm.
        
        Args:
            x: Input vector
            alpha: Scaling factor
            
        Returns:
            bool: True if absolute homogeneity holds, False otherwise
        """
        self.logger.debug(f"Checking absolute homogeneity with alpha {alpha}")
        norm_x = self.compute(x)
        norm_alpha_x = self.compute(alpha * x)
        return norm_alpha_x == abs(alpha) * norm_x

    def check_definiteness(self, x: T) -> bool:
        """
        Verifies the definiteness property of the norm.
        
        A norm is definite if norm(x) = 0 if and only if x = 0.
        
        Args:
            x: Input vector
            
        Returns:
            bool: True if definiteness holds, False otherwise
        """
        self.logger.debug("Checking definiteness property")
        norm = self.compute(x)
        if norm == 0:
            return x == 0
        return True

logger = logging.getLogger(__name__)