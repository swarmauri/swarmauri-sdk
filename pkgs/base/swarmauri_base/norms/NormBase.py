from typing import Any, List, Optional, Tuple, TypeVar, Union, Generic
import numpy as np
import logging
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.norms.INorm import INorm, T

# Configure logging
logger = logging.getLogger(__name__)

@ComponentBase.register_model()
class NormBase(INorm[T], ComponentBase):
    """
    Base class for norm implementations.
    
    This class provides a concrete implementation of the INorm interface,
    serving as a template for specific norm behaviors. It implements
    common normalization patterns across vector norms.
    
    Attributes
    ----------
    resource : str
        Resource type identifier, defaults to 'norm'
    """
    resource: Optional[str] = Field(default=ResourceTypes.NORM.value)
    
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
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError("Method 'compute' must be implemented by subclasses")
    
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
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError("Method 'distance' must be implemented by subclasses")
    
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
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError("Method 'normalize' must be implemented by subclasses")
    
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
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError("Method 'is_normalized' must be implemented by subclasses")
    
    def name(self) -> str:
        """
        Get the name of this norm implementation.
        
        Returns
        -------
        str
            String identifier for this norm
            
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        raise NotImplementedError("Method 'name' must be implemented by subclasses")