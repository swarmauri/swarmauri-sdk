from abc import ABC, abstractmethod
import logging
from typing import Any, TypeVar, Generic, Optional

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for generic typing
T = TypeVar('T')
V = TypeVar('V')


class IInnerProduct(Generic[T, V], ABC):
    """
    Abstract interface for inner product operations.
    
    This interface defines the contract for inner product calculations
    between elements of a vector space.
    """
    
    @abstractmethod
    def compute(self, left: T, right: T) -> V:
        """
        Compute the inner product between two elements.
        
        Parameters
        ----------
        left : T
            The left element in the inner product
        right : T
            The right element in the inner product
            
        Returns
        -------
        V
            The result of the inner product calculation
        """
        pass


class IUseInnerProduct(ABC):
    """
    Abstract interface marking components using inner product geometry.
    
    This interface indicates a dependency on inner product structure and
    should be implemented by components that rely on inner product operations
    for their functionality.
    """
    
    @abstractmethod
    def get_inner_product(self) -> Optional[IInnerProduct]:
        """
        Get the inner product implementation used by this component.
        
        Returns
        -------
        Optional[IInnerProduct]
            The inner product implementation or None if not set
        """
        pass
    
    @abstractmethod
    def set_inner_product(self, inner_product: IInnerProduct) -> None:
        """
        Set the inner product implementation to be used by this component.
        
        Parameters
        ----------
        inner_product : IInnerProduct
            The inner product implementation to use
        """
        pass
    
    @abstractmethod
    def requires_inner_product(self) -> bool:
        """
        Check if this component requires an inner product to function.
        
        Returns
        -------
        bool
            True if an inner product is required, False otherwise
        """
        pass