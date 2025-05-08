from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic

import logging

# Define a generic type for vectors
T = TypeVar('T')

class IInnerProduct(Generic[T], ABC):
    """
    Interface for inner product operations between vectors.
    
    This abstract class defines the contract for computing inner products
    between vectors in a vector space. Implementations must ensure that
    the inner product satisfies the mathematical properties of inner products:
    - Linearity in the first argument
    - Conjugate symmetry (if applicable)
    - Positive definiteness
    """
    
    def __init__(self) -> None:
        """
        Initialize the inner product implementation.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Initializing inner product interface")
    
    @abstractmethod
    def compute(self, vec1: T, vec2: T) -> float:
        """
        Compute the inner product between two vectors.
        
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
        ValueError
            If the vectors are incompatible for inner product calculation
        TypeError
            If the vectors are of unsupported types
        """
        pass
    
    @abstractmethod
    def is_compatible(self, vec1: T, vec2: T) -> bool:
        """
        Check if two vectors are compatible for inner product calculation.
        
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
        """
        pass