from typing import Any, Literal, Optional, TypeVar, Union, Generic
import numpy as np
import logging
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.norms.NormBase import NormBase, T

# Configure logging
logger = logging.getLogger(__name__)

@ComponentBase.register_type(NormBase, "LInfNorm")
class LInfNorm(NormBase):
    """
    Implementation of the supremum (L-infinity) norm.
    
    The L-infinity norm measures the largest absolute value in a function's domain.
    This implementation works with numpy arrays, lists, and other array-like objects.
    
    Attributes
    ----------
    type : Literal["LInfNorm"]
        Type identifier for this norm implementation
    resource : str
        Resource type identifier, defaults to 'norm'
    """
    type: Literal["LInfNorm"] = "LInfNorm"
    resource: Optional[str] = Field(default=ResourceTypes.NORM.value)
    
    def compute(self, x: T) -> float:
        """
        Compute the L-infinity norm of a vector.
        
        The L-infinity norm is the maximum absolute value of the elements in x.
        
        Parameters
        ----------
        x : T
            Vector-like object whose norm is to be calculated
            
        Returns
        -------
        float
            The maximum absolute value in x
            
        Raises
        ------
        ValueError
            If input is not a valid vector-like object
        TypeError
            If input type is not supported
        """
        try:
            # Convert input to numpy array if it isn't already
            x_array = np.asarray(x, dtype=float)
            
            # Check if the domain is bounded
            if not np.all(np.isfinite(x_array)):
                raise ValueError("Domain must be bounded for L-infinity norm computation")
                
            # Compute the maximum absolute value
            result = np.max(np.abs(x_array))
            logger.debug(f"Computed L-infinity norm: {result}")
            return float(result)
        except Exception as e:
            logger.error(f"Error computing L-infinity norm: {str(e)}")
            raise
    
    def distance(self, x: T, y: T) -> float:
        """
        Compute the distance between two vectors using the L-infinity norm.
        
        The L-infinity distance is the maximum absolute difference between 
        corresponding elements of x and y.
        
        Parameters
        ----------
        x : T
            First vector
        y : T
            Second vector
            
        Returns
        -------
        float
            The maximum absolute difference between elements of x and y
            
        Raises
        ------
        ValueError
            If inputs are not valid vector-like objects or have incompatible dimensions
        TypeError
            If input types are not supported
        """
        try:
            # Convert inputs to numpy arrays
            x_array = np.asarray(x, dtype=float)
            y_array = np.asarray(y, dtype=float)
            
            # Check if the domains are bounded
            if not (np.all(np.isfinite(x_array)) and np.all(np.isfinite(y_array))):
                raise ValueError("Domains must be bounded for L-infinity distance computation")
            
            # Check if dimensions match
            if x_array.shape != y_array.shape:
                raise ValueError(f"Input vectors have incompatible dimensions: {x_array.shape} vs {y_array.shape}")
            
            # Compute the maximum absolute difference
            result = np.max(np.abs(x_array - y_array))
            logger.debug(f"Computed L-infinity distance: {result}")
            return float(result)
        except Exception as e:
            logger.error(f"Error computing L-infinity distance: {str(e)}")
            raise
    
    def normalize(self, x: T) -> T:
        """
        Normalize a vector to have unit L-infinity norm.
        
        The normalized vector has the same direction as x but with a maximum 
        absolute value of 1.
        
        Parameters
        ----------
        x : T
            Vector to normalize
            
        Returns
        -------
        T
            Normalized vector with the same type as the input
            
        Raises
        ------
        ValueError
            If input is a zero vector or not a valid vector-like object
        TypeError
            If input type is not supported
        """
        try:
            # Convert input to numpy array
            x_array = np.asarray(x, dtype=float)
            
            # Check if the domain is bounded
            if not np.all(np.isfinite(x_array)):
                raise ValueError("Domain must be bounded for L-infinity normalization")
            
            # Compute the norm
            norm_value = self.compute(x_array)
            
            # Check for zero vector
            if norm_value == 0:
                raise ValueError("Cannot normalize a zero vector")
            
            # Normalize by dividing by the norm
            normalized = x_array / norm_value
            
            logger.debug(f"Normalized vector with L-infinity norm")
            
            # Return in the same format as the input
            if isinstance(x, list):
                return normalized.tolist()
            elif isinstance(x, np.ndarray):
                return normalized
            else:
                # Try to convert back to the original type
                return type(x)(normalized)
        except Exception as e:
            logger.error(f"Error normalizing with L-infinity norm: {str(e)}")
            raise
    
    def is_normalized(self, x: T, tolerance: float = 1e-10) -> bool:
        """
        Check if a vector has unit L-infinity norm within a given tolerance.
        
        Parameters
        ----------
        x : T
            Vector to check
        tolerance : float, optional
            Tolerance for floating-point comparison, by default 1e-10
            
        Returns
        -------
        bool
            True if the vector's L-infinity norm is within tolerance of 1.0, False otherwise
            
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
            
            # Check if it's close to 1.0
            is_unit = abs(norm_value - 1.0) <= tolerance
            
            logger.debug(f"Checked if vector is normalized (L-infinity norm): {is_unit}")
            return is_unit
        except Exception as e:
            logger.error(f"Error checking normalization with L-infinity norm: {str(e)}")
            raise
    
    def name(self) -> str:
        """
        Get the name of this norm implementation.
        
        Returns
        -------
        str
            String identifier for this norm
        """
        return "L-infinity norm"