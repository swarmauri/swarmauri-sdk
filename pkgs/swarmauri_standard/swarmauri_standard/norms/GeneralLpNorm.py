from typing import TypeVar, Union
import logging
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from base.swarmauri_base.norms.NormBase import NormBase

T = TypeVar('T', Union['IVector', 'IMatrix', str, bytes, Sequence, Callable])

@ComponentBase.register_type(NormBase, "GeneralLpNorm")
class GeneralLpNorm(NormBase):
    """
    A concrete implementation of the Lp norm for p in (1, ∞). This class provides 
    the functionality to compute the Lp norm of various types of inputs, including 
    vectors, matrices, strings, bytes, sequences, and callables.
    
    Inherits From:
        NormBase: Abstract base class for norm computations.
        ComponentBase: Base class for all components in the system.
    """
    p: float = Field(..., gt=1, le=math.inf)
    type: Literal["GeneralLpNorm"] = "GeneralLpNorm"
    resource: Optional[str] = Field(default=ResourceTypes.NORM.value)
    
    def __init__(self, p: float):
        """
        Initializes the GeneralLpNorm instance with the specified p value.
        
        Args:
            p: float
                The parameter of the Lp norm. Must be greater than 1 and finite.
                
        Raises:
            ValueError: If p is not greater than 1 or not finite.
        """
        super().__init__()
        if not (1 < p < math.inf):
            raise ValueError("p must be greater than 1 and finite")
        self.p = p
        logger.debug("GeneralLpNorm instance initialized with p = %s", p)
        
    def compute(self, x: T) -> float:
        """
        Computes the Lp norm of the given input.
        
        Args:
            x: T
                The input to compute the norm for. Can be a vector, matrix, 
                string, bytes, sequence, or callable.
                
        Returns:
            float:
                The computed Lp norm value
                
        Raises:
            ValueError: If the input cannot be processed
        """
        logger.debug("Computing Lp norm with p = %s", self.p)
        try:
            # Assuming x is an iterable or has a length
            elements = (abs(element) ** self.p for element in x)
            sum_elements = sum(elements)
            return sum_elements ** (1.0 / self.p)
        except Exception as e:
            logger.error("Failed to compute Lp norm: %s", str(e))
            raise ValueError("Failed to compute Lp norm") from e
            
    def check_non_negativity(self, x: T) -> bool:
        """
        Checks if the Lp norm satisfies non-negativity.
        
        Args:
            x: T
                The input to check
                
        Returns:
            bool:
                True if the norm is non-negative, False otherwise
                
        Raises:
            ValueError: If the input cannot be processed
        """
        logger.debug("Checking non-negativity of Lp norm")
        try:
            norm = self.compute(x)
            return norm >= 0
        except ValueError as e:
            logger.error("Failed to check non-negativity: %s", str(e))
            raise

    def check_triangle_inequality(self, x: T, y: T) -> bool:
        """
        Checks if the Lp norm satisfies the triangle inequality.
        
        Args:
            x: T
                The first input vector/matrix
            y: T
                The second input vector/matrix
                
        Returns:
            bool:
                True if ||x + y|| <= ||x|| + ||y||, False otherwise
                
        Raises:
            ValueError: If the input cannot be processed
        """
        logger.debug("Checking triangle inequality of Lp norm")
        try:
            norm_x = self.compute(x)
            norm_y = self.compute(y)
            combined = x + y  # type: ignore
            norm_combined = self.compute(combined)
            return norm_combined <= norm_x + norm_y
        except ValueError as e:
            logger.error("Failed to check triangle inequality: %s", str(e))
            raise

    def check_absolute_homogeneity(self, x: T, scalar: float) -> bool:
        """
        Checks if the Lp norm satisfies absolute homogeneity.
        
        Args:
            x: T
                The input to check
            scalar: float
                The scalar to scale with
                
        Returns:
            bool:
                True if ||c * x|| = |c| * ||x||, False otherwise
                
        Raises:
            ValueError: If the input cannot be processed
        """
        logger.debug("Checking absolute homogeneity of Lp norm")
        try:
            scaled_x = scalar * x  # type: ignore
            norm_scaled = self.compute(scaled_x)
            norm_x = self.compute(x)
            return norm_scaled == abs(scalar) * norm_x
        except ValueError as e:
            logger.error("Failed to check absolute homogeneity: %s", str(e))
            raise

    def check_definiteness(self, x: T) -> bool:
        """
        Checks if the Lp norm is definite (norm(x) = 0 if and only if x = 0).
        
        Args:
            x: T
                The input to check
                
        Returns:
            bool:
                True if norm(x) = 0 implies x = 0, False otherwise
                
        Raises:
            ValueError: If the input cannot be processed
        """
        logger.debug("Checking definiteness of Lp norm")
        try:
            norm = self.compute(x)
            return norm == 0
        except ValueError as e:
            logger.error("Failed to check definiteness: %s", str(e))
            raise

# Initialize logger
logger = logging.getLogger(__name__)