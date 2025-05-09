from typing import Optional, TypeVar, Union
from pydantic import Field
import logging
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.norms.INorm import INorm

T = TypeVar('T', Union['IVector', 'IMatrix', str, bytes, Sequence, Callable])

@ComponentBase.register_model()
class NormBase(INorm, ComponentBase):
    """
    Base class providing template logic for norm behaviors. This class implements 
    common interfaces for norm computations and provides a foundation for 
    concrete norm implementations.
    
    Inherits From:
        INorm: Interface for norm computations on vector spaces.
        ComponentBase: Base class for all components in the system.
    """
    resource: Optional[str] = Field(default=ResourceTypes.NORM.value)
    
    def __init__(self):
        """
        Initializes the NormBase instance.
        
        Raises:
            NotImplementedError: This class is a base class and should not be 
                instantiated directly.
        """
        super().__init__()
        logger.debug("NormBase instance initialized")
        raise NotImplementedError("This class is a base class and should not be instantiated directly")

    def compute(self, x: T) -> float:
        """
        Template method for computing the norm of the given input.
        
        Args:
            x: T
                The input to compute the norm for. Can be a vector, matrix, 
                string, bytes, sequence, or callable.
                
        Returns:
            float:
                The computed norm value
                
        Raises:
            NotImplementedError: Method must be implemented in subclass
        """
        logger.debug("Computing norm")
        raise NotImplementedError("Method 'compute' must be implemented in subclass")

    def check_non_negativity(self, x: T) -> bool:
        """
        Template method for checking if the norm satisfies non-negativity.
        
        Args:
            x: T
                The input to check
                
        Returns:
            bool:
                True if norm(x) >= 0, False otherwise
                
        Raises:
            NotImplementedError: Method must be implemented in subclass
        """
        logger.debug("Checking non-negativity")
        raise NotImplementedError("Method 'check_non_negativity' must be implemented in subclass")

    def check_triangle_inequality(self, x: T, y: T) -> bool:
        """
        Template method for checking if the norm satisfies the triangle inequality.
        
        Args:
            x: T
                The first input vector/matrix
            y: T
                The second input vector/matrix
                
        Returns:
            bool:
                True if ||x + y|| <= ||x|| + ||y||, False otherwise
                
        Raises:
            NotImplementedError: Method must be implemented in subclass
        """
        logger.debug("Checking triangle inequality")
        raise NotImplementedError("Method 'check_triangle_inequality' must be implemented in subclass")

    def check_absolute_homogeneity(self, x: T, scalar: float) -> bool:
        """
        Template method for checking if the norm satisfies absolute homogeneity.
        
        Args:
            x: T
                The input to check
            scalar: float
                The scalar to scale with
                
        Returns:
            bool:
                True if ||c * x|| = |c| * ||x||, False otherwise
                
        Raises:
            NotImplementedError: Method must be implemented in subclass
        """
        logger.debug("Checking absolute homogeneity")
        raise NotImplementedError("Method 'check_absolute_homogeneity' must be implemented in subclass")

    def check_definiteness(self, x: T) -> bool:
        """
        Template method for checking if the norm is definite (norm(x) = 0 if and only if x = 0).
        
        Args:
            x: T
                The input to check
                
        Returns:
            bool:
                True if norm(x) = 0 implies x = 0, False otherwise
                
        Raises:
            NotImplementedError: Method must be implemented in subclass
        """
        logger.debug("Checking definiteness")
        raise NotImplementedError("Method 'check_definiteness' must be implemented in subclass")