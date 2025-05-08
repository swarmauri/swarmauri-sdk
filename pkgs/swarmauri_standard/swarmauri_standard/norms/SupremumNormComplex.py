from typing import Any, List, Optional, Tuple, TypeVar, Union, Literal, cast, Type
import numpy as np
import logging
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.norms.NormBase import NormBase, T

# Configure logging
logger = logging.getLogger(__name__)


@ComponentBase.register_type(NormBase, "SupremumNormComplex")
class SupremumNormComplex(NormBase):
    """
    Supremum norm implementation for complex-valued functions.
    
    This class implements the supremum norm (also known as the maximum norm or infinity norm)
    for complex-valued functions. It computes the maximum absolute value of a complex vector
    or array within the specified interval.
    
    Attributes
    ----------
    type : Literal["SupremumNormComplex"]
        Type identifier for this norm implementation
    """
    type: Literal["SupremumNormComplex"] = "SupremumNormComplex"
    
    def compute(self, x: T) -> float:
        """
        Compute the supremum norm (maximum absolute value) of a complex vector.
        
        Parameters
        ----------
        x : T
            Complex vector-like object whose norm is to be calculated
            
        Returns
        -------
        float
            The maximum absolute value of the elements in x
            
        Raises
        ------
        ValueError
            If input is not a valid vector-like object
        TypeError
            If input type is not supported
        """
        logger.debug(f"Computing supremum norm for complex vector of shape {np.shape(x)}")
        
        try:
            # Convert input to numpy array if it's not already
            x_array = np.asarray(x, dtype=complex)
            
            # Compute the absolute values of all elements
            abs_values = np.abs(x_array)
            
            # Return the maximum value
            result = float(np.max(abs_values))
            logger.debug(f"Supremum norm result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error computing supremum norm: {str(e)}")
            raise ValueError(f"Failed to compute supremum norm: {str(e)}")
    
    def distance(self, x: T, y: T) -> float:
        """
        Compute the distance between two complex vectors using the supremum norm.
        
        The distance is defined as the maximum absolute value of their element-wise difference.
        
        Parameters
        ----------
        x : T
            First complex vector
        y : T
            Second complex vector
            
        Returns
        -------
        float
            The maximum absolute value of the difference between x and y
            
        Raises
        ------
        ValueError
            If inputs are not valid vector-like objects or have incompatible dimensions
        TypeError
            If input types are not supported
        """
        logger.debug(f"Computing supremum norm distance between vectors")
        
        try:
            # Convert inputs to numpy arrays
            x_array = np.asarray(x, dtype=complex)
            y_array = np.asarray(y, dtype=complex)
            
            # Check if shapes are compatible
            if x_array.shape != y_array.shape:
                raise ValueError(f"Incompatible shapes: {x_array.shape} and {y_array.shape}")
            
            # Compute the element-wise difference
            diff = x_array - y_array
            
            # Return the supremum norm of the difference
            return self.compute(diff)
            
        except Exception as e:
            logger.error(f"Error computing supremum norm distance: {str(e)}")
            raise ValueError(f"Failed to compute supremum norm distance: {str(e)}")
    
    def normalize(self, x: T) -> T:
        """
        Normalize a complex vector to have unit supremum norm.
        
        Parameters
        ----------
        x : T
            Complex vector to normalize
            
        Returns
        -------
        T
            Normalized complex vector with the same direction as x but unit supremum norm
            
        Raises
        ------
        ValueError
            If input is a zero vector or not a valid vector-like object
        TypeError
            If input type is not supported
        """
        logger.debug(f"Normalizing complex vector using supremum norm")
        
        try:
            # Convert input to numpy array
            x_array = np.asarray(x, dtype=complex)
            
            # Compute the norm
            norm_value = self.compute(x_array)
            
            # Check if the norm is zero
            if norm_value == 0 or np.isclose(norm_value, 0):
                raise ValueError("Cannot normalize a zero vector")
            
            # Normalize the vector
            normalized = x_array / norm_value
            
            # Convert back to the original type if possible
            if isinstance(x, np.ndarray):
                return normalized
            elif isinstance(x, list):
                return normalized.tolist()
            else:
                # Try to cast to the original type, otherwise return as numpy array
                try:
                    return type(x)(normalized)
                except:
                    return normalized
                
        except Exception as e:
            logger.error(f"Error normalizing with supremum norm: {str(e)}")
            raise ValueError(f"Failed to normalize with supremum norm: {str(e)}")
    
    def is_normalized(self, x: T, tolerance: float = 1e-10) -> bool:
        """
        Check if a complex vector has unit supremum norm within a given tolerance.
        
        Parameters
        ----------
        x : T
            Complex vector to check
        tolerance : float, optional
            Tolerance for floating-point comparison, by default 1e-10
            
        Returns
        -------
        bool
            True if the vector's supremum norm is within tolerance of 1.0, False otherwise
            
        Raises
        ------
        ValueError
            If input is not a valid vector-like object
        TypeError
            If input type is not supported
        """
        logger.debug(f"Checking if complex vector is normalized with tolerance {tolerance}")
        
        try:
            # Compute the norm
            norm_value = self.compute(x)
            
            # Check if the norm is close to 1.0
            is_unit_norm = np.isclose(norm_value, 1.0, atol=tolerance)
            logger.debug(f"Vector has norm {norm_value}, is normalized: {is_unit_norm}")
            
            return is_unit_norm
            
        except Exception as e:
            logger.error(f"Error checking normalization: {str(e)}")
            raise ValueError(f"Failed to check if vector is normalized: {str(e)}")
    
    def name(self) -> str:
        """
        Get the name of this norm implementation.
        
        Returns
        -------
        str
            String identifier for this norm
        """
        return "SupremumNormComplex"