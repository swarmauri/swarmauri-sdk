from abc import ABC, abstractmethod
from typing import Type, Literal
import logging
from swarmauri_core.inner_products.IInnerProduct import IInnerProduct
from swarmauri_core.vectors.IVector import IVector

logger = logging.getLogger(__name__)


class IUseInnerProduct(ABC):
    """Abstract interface marking components using inner product geometry.
    
    This interface defines the contract for components that depend on inner product
    operations. It provides abstract methods for checking key geometric properties
    enabled by the inner product structure.
    """
    
    def __init__(self, inner_product: Type[IInnerProduct]):
        """Initialize with a compatible inner product implementation.
        
        Args:
            inner_product: Implementation of IInnerProduct to use for operations
        """
        self.inner_product = inner_product()
        
    @abstractmethod
    def check_angle_between_vectors(self, x: IVector, y: IVector) -> float:
        """Compute the angle between two vectors using the inner product.
        
        Args:
            x: First vector
            y: Second vector
            
        Returns:
            Angle in radians between the two vectors
        """
        pass
    
    @abstractmethod
    def check_verify_orthogonality(self, x: IVector, y: IVector) -> bool:
        """Verify if two vectors are orthogonal using the inner product.
        
        Args:
            x: First vector
            y: Second vector
            
        Returns:
            True if vectors are orthogonal (inner product is zero), False otherwise
        """
        pass
    
    @abstractmethod
    def check_xy_project(self, x: IVector, y: IVector) -> IVector:
        """Project vector x onto vector y using the inner product.
        
        Args:
            x: Vector to project
            y: Vector onto which to project
            
        Returns:
            Projection of x onto y
        """
        pass
    
    @abstractmethod
    def check_verify_parallelogram_law(self, x: IVector, y: IVector) -> bool:
        """Verify the parallelogram law using the inner product.
        
        The parallelogram law states that:
        ||x + y||² + ||x - y||² = 2||x||² + 2||y||²
        
        Args:
            x: First vector
            y: Second vector
            
        Returns:
            True if the parallelogram law holds, False otherwise
        """
        pass