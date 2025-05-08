from typing import TypeVar, Generic, Any
import logging
from abc import ABC

from swarmauri_core.inner_products.IInnerProduct import IInnerProduct, T
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

@ComponentBase.register_model()
class InnerProductBase(IInnerProduct[T], ComponentBase):
    """
    Abstract base class implementing partial methods for inner product calculation.
    
    This class provides reusable logic for inner product implementations and serves
    as a foundation for specific inner product implementations. It inherits from
    IInnerProduct and implements the required abstract methods, raising
    NotImplementedError to indicate that concrete subclasses must provide
    the actual implementation.
    
    Attributes
    ----------
    resource : str
        The resource type identifier for this component
    """
    
    resource: str = ResourceTypes.INNER_PRODUCT.value
    
    def __init__(self) -> None:
        """
        Initialize the inner product base implementation.
        
        Sets up logging and initializes the base class.
        """
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Initializing InnerProductBase")
    
    def compute(self, vec1: T, vec2: T) -> float:
        """
        Compute the inner product between two vectors.
        
        This is an abstract method that must be implemented by concrete subclasses.
        
        Parameters
        ----------
        vec1 : T
            First vector in the inner product
        vec2 : T
            Second vector in the inner product
            
        Returns
        -------
        float
            The resulting inner product value
            
        Raises
        ------
        NotImplementedError
            This base method must be overridden by subclasses
        ValueError
            If the vectors are incompatible for inner product calculation
        TypeError
            If the vectors are of unsupported types
        """
        self.logger.error("compute method not implemented")
        raise NotImplementedError("compute method must be implemented by subclasses")
    
    def is_compatible(self, vec1: T, vec2: T) -> bool:
        """
        Check if two vectors are compatible for inner product calculation.
        
        This is an abstract method that must be implemented by concrete subclasses.
        
        Parameters
        ----------
        vec1 : T
            First vector to check
        vec2 : T
            Second vector to check
            
        Returns
        -------
        bool
            True if the vectors are compatible, False otherwise
            
        Raises
        ------
        NotImplementedError
            This base method must be overridden by subclasses
        """
        self.logger.error("is_compatible method not implemented")
        raise NotImplementedError("is_compatible method must be implemented by subclasses")