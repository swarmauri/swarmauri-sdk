from typing import Any, List, Optional, Tuple, TypeVar, Union, Generic, Literal
import numpy as np
import logging
from pydantic import Field, validator

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.norms.NormBase import NormBase
from swarmauri_core.norms.INorm import T

# Configure logging
logger = logging.getLogger(__name__)


@ComponentBase.register_type(NormBase, "GeneralLpNorm")
class GeneralLpNorm(NormBase):
    """
    Implementation of the Lp norm with parameter p in (1, ∞).
    
    The Lp norm of a vector x is defined as:
    ||x||_p = (sum_i |x_i|^p)^(1/p)
    
    This class implements the Lp norm for any real value of p greater than 1.
    
    Attributes
    ----------
    type : Literal["GeneralLpNorm"]
        Type identifier for this norm implementation
    p : float
        The parameter p of the Lp norm, must be greater than 1
    """
    type: Literal["GeneralLpNorm"] = "GeneralLpNorm"
    p: float = Field(default=2.0, description="Parameter p for the Lp norm, must be > 1")
    
    @validator('p')
    def validate_p(cls, p_value):
        """
        Validate that p is greater than 1.
        
        Parameters
        ----------
        p_value : float
            Value of p to validate
            
        Returns
        -------
        float
            The validated p value
            
        Raises
        ------
        ValueError
            If p is not greater than 1
        """
        if p_value <= 1:
            raise ValueError(f"Parameter p must be greater than 1, got {p_value}")
        return p_value
    
    def compute(self, x: T) -> float:
        """
        Compute the Lp norm of a vector.
        
        Parameters
        ----------
        x : T
            Vector-like object whose norm is to be calculated
            
        Returns
        -------
        float
            The Lp norm value
            
        Raises
        ------
        ValueError
            If input is not a valid vector-like object
        TypeError
            If input type is not supported
        """
        try:
            # Convert input to numpy array for consistent handling
            x_array = np.asarray(x, dtype=np.float64)
            
            # Compute the Lp norm: (sum(|x_i|^p))^(1/p)
            norm_value = np.sum(np.abs(x_array) ** self.p) ** (1.0 / self.p)
            
            logger.debug(f"Computed Lp norm with p={self.p}: {norm_value}")
            return float(norm_value)
        except Exception as e:
            logger.error(f"Error computing Lp norm: {str(e)}")
            raise ValueError(f"Failed to compute Lp norm: {str(e)}")
    
    def distance(self, x: T, y: T) -> float:
        """
        Compute the distance between two vectors using this Lp norm.
        
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
            The Lp distance between x and y
            
        Raises
        ------
        ValueError
            If inputs are not valid vector-like objects or have incompatible dimensions
        TypeError
            If input types are not supported
        """
        try:
            # Convert inputs to numpy arrays for consistent handling
            x_array = np.asarray(x, dtype=np.float64)
            y_array = np.asarray(y, dtype=np.float64)
            
            # Check if dimensions are compatible
            if x_array.shape != y_array.shape:
                raise ValueError(f"Incompatible dimensions: {x_array.shape} and {y_array.shape}")
            
            # Compute the Lp distance: ||x - y||_p
            distance_value = self.compute(x_array - y_array)
            
            logger.debug(f"Computed Lp distance with p={self.p}: {distance_value}")
            return float(distance_value)
        except Exception as e:
            logger.error(f"Error computing Lp distance: {str(e)}")
            raise ValueError(f"Failed to compute Lp distance: {str(e)}")
    
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
            Normalized vector with the same direction as x but unit Lp norm
            
        Raises
        ------
        ValueError
            If input is a zero vector or not a valid vector-like object
        TypeError
            If input type is not supported
        """
        try:
            # Convert input to numpy array for consistent handling
            x_array = np.asarray(x, dtype=np.float64)
            
            # Compute the norm
            norm_value = self.compute(x_array)
            
            # Check if the vector is non-zero
            if norm_value < np.finfo(float).eps:
                raise ValueError("Cannot normalize a zero vector")
            
            # Normalize the vector
            normalized = x_array / norm_value
            
            logger.debug(f"Normalized vector using Lp norm with p={self.p}")
            
            # Return the same type as the input
            if isinstance(x, list):
                return normalized.tolist()
            elif isinstance(x, tuple):
                return tuple(normalized.tolist())
            else:
                return normalized
        except Exception as e:
            logger.error(f"Error normalizing vector: {str(e)}")
            raise ValueError(f"Failed to normalize vector: {str(e)}")
    
    def is_normalized(self, x: T, tolerance: float = 1e-10) -> bool:
        """
        Check if a vector has unit Lp norm within a given tolerance.
        
        Parameters
        ----------
        x : T
            Vector to check
        tolerance : float, optional
            Tolerance for floating-point comparison, by default 1e-10
            
        Returns
        -------
        bool
            True if the vector's Lp norm is within tolerance of 1.0, False otherwise
            
        Raises
        ------
        ValueError
            If input is not a valid vector-like object
        TypeError
            If input type is not supported
        """
        try:
            # Compute the norm
            norm_value = self.compute(x)
            
            # Check if the norm is close to 1.0
            is_unit_norm = abs(norm_value - 1.0) <= tolerance
            
            logger.debug(f"Vector Lp norm: {norm_value}, is normalized: {is_unit_norm}")
            return is_unit_norm
        except Exception as e:
            logger.error(f"Error checking if vector is normalized: {str(e)}")
            raise ValueError(f"Failed to check if vector is normalized: {str(e)}")
    
    def name(self) -> str:
        """
        Get the name of this norm implementation.
        
        Returns
        -------
        str
            String identifier for this Lp norm
        """
        return f"L{self.p} Norm"