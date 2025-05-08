from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic, Union, List, Tuple
import numpy as np
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Type variable for vector-like objects
T = TypeVar('T', bound=Union[np.ndarray, List[float], Tuple[float, ...]])

class INorm(ABC, Generic[T]):
    """
    Interface for norm computations on vector spaces.
    
    This abstract base class defines the contract for norm behavior, 
    enforcing point-separating distance logic in vector spaces.
    
    A norm must satisfy the following properties:
    1. Non-negativity: norm(x) >= 0 for all x
    2. Definiteness: norm(x) = 0 if and only if x = 0
    3. Triangle inequality: norm(x + y) <= norm(x) + norm(y)
    4. Homogeneity: norm(a*x) = |a|*norm(x) for scalar a
    """

    @abstractmethod
    def compute(self, x: T) -> float:
        """
        Compute the norm of a vector.
        
        Parameters
        ----------
        x : T
            Vector-like object whose norm is to be calculated
            
        Returns
        -------
        float
            The norm value, satisfying non-negativity and definiteness
            
        Raises
        ------
        ValueError
            If input is not a valid vector-like object
        TypeError
            If input type is not supported
        """
        pass
    
    @abstractmethod
    def distance(self, x: T, y: T) -> float:
        """
        Compute the distance between two vectors using this norm.
        
        The distance between vectors x and y is defined as the norm of their difference.
        
        Parameters
        ----------
        x : T
            First vector
        y : T
            Second vector
            
        Returns
        -------
        float
            The distance between x and y, satisfying the triangle inequality
            
        Raises
        ------
        ValueError
            If inputs are not valid vector-like objects or have incompatible dimensions
        TypeError
            If input types are not supported
        """
        pass
    
    @abstractmethod
    def normalize(self, x: T) -> T:
        """
        Normalize a vector to have unit norm.
        
        Parameters
        ----------
        x : T
            Vector to normalize
            
        Returns
        -------
        T
            Normalized vector with the same direction as x but unit norm
            
        Raises
        ------
        ValueError
            If input is a zero vector or not a valid vector-like object
        TypeError
            If input type is not supported
        """
        pass
    
    @abstractmethod
    def is_normalized(self, x: T, tolerance: float = 1e-10) -> bool:
        """
        Check if a vector has unit norm within a given tolerance.
        
        Parameters
        ----------
        x : T
            Vector to check
        tolerance : float, optional
            Tolerance for floating-point comparison, by default 1e-10
            
        Returns
        -------
        bool
            True if the vector's norm is within tolerance of 1.0, False otherwise
            
        Raises
        ------
        ValueError
            If input is not a valid vector-like object
        TypeError
            If input type is not supported
        """
        pass
    
    @abstractmethod
    def name(self) -> str:
        """
        Get the name of this norm implementation.
        
        Returns
        -------
        str
            String identifier for this norm
        """
        pass