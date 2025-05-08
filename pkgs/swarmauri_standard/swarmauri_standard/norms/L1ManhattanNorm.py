from typing import Any, List, Optional, Tuple, TypeVar, Union, Generic, Literal
import numpy as np
import logging
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.norms.NormBase import NormBase, T

# Configure logging
logger = logging.getLogger(__name__)

@ComponentBase.register_type(NormBase, "L1ManhattanNorm")
class L1ManhattanNorm(NormBase):
    """
    L1 (Manhattan) norm implementation.
    
    This class computes the L1 norm of vectors, also known as the Manhattan norm,
    which is the sum of the absolute values of vector components.
    
    Attributes
    ----------
    type : Literal["L1ManhattanNorm"]
        The type identifier for this norm implementation
    resource : str
        Resource type identifier, defaults to 'norm'
    """
    type: Literal["L1ManhattanNorm"] = "L1ManhattanNorm"
    resource: Optional[str] = Field(default=ResourceTypes.NORM.value)
    
    def compute(self, x: T) -> float:
        """
        Compute the L1 (Manhattan) norm of a vector.
        
        Parameters
        ----------
        x : T
            Vector-like object whose L1 norm is to be calculated
            
        Returns
        -------
        float
            The L1 norm value, which is the sum of absolute values of components
            
        Raises
        ------
        ValueError
            If input is not a valid vector-like object
        TypeError
            If input type is not supported
        """
        logger.debug(f"Computing L1 norm for vector of type {type(x)}")
        
        # Convert input to numpy array if it's not already
        if not isinstance(x, np.ndarray):
            try:
                x = np.array(x, dtype=float)
            except (ValueError, TypeError) as e:
                logger.error(f"Failed to convert input to numpy array: {e}")
                raise TypeError(f"Input must be convertible to numpy array: {e}")
        
        # Ensure input is a vector (1D array or 2D array with one dimension of size 1)
        if x.ndim > 2 or (x.ndim == 2 and min(x.shape) > 1):
            logger.error(f"Input has invalid shape: {x.shape}")
            raise ValueError(f"Input must be a vector, got shape {x.shape}")
        
        # Flatten to 1D array for consistent processing
        x_flat = x.flatten()
        
        # Compute L1 norm: sum of absolute values
        norm_value = np.sum(np.abs(x_flat))
        
        logger.debug(f"L1 norm computed: {norm_value}")
        return float(norm_value)
    
    def distance(self, x: T, y: T) -> float:
        """
        Compute the L1 (Manhattan) distance between two vectors.
        
        Parameters
        ----------
        x : T
            First vector
        y : T
            Second vector
            
        Returns
        -------
        float
            The L1 distance between x and y, which is the sum of absolute differences
            
        Raises
        ------
        ValueError
            If inputs are not valid vector-like objects or have incompatible dimensions
        TypeError
            If input types are not supported
        """
        logger.debug(f"Computing L1 distance between vectors of types {type(x)} and {type(y)}")
        
        # Convert inputs to numpy arrays if they're not already
        if not isinstance(x, np.ndarray):
            try:
                x = np.array(x, dtype=float)
            except (ValueError, TypeError) as e:
                logger.error(f"Failed to convert first input to numpy array: {e}")
                raise TypeError(f"First input must be convertible to numpy array: {e}")
                
        if not isinstance(y, np.ndarray):
            try:
                y = np.array(y, dtype=float)
            except (ValueError, TypeError) as e:
                logger.error(f"Failed to convert second input to numpy array: {e}")
                raise TypeError(f"Second input must be convertible to numpy array: {e}")
        
        # Ensure inputs are vectors
        if x.ndim > 2 or (x.ndim == 2 and min(x.shape) > 1):
            logger.error(f"First input has invalid shape: {x.shape}")
            raise ValueError(f"First input must be a vector, got shape {x.shape}")
            
        if y.ndim > 2 or (y.ndim == 2 and min(y.shape) > 1):
            logger.error(f"Second input has invalid shape: {y.shape}")
            raise ValueError(f"Second input must be a vector, got shape {y.shape}")
        
        # Flatten to 1D arrays for consistent processing
        x_flat = x.flatten()
        y_flat = y.flatten()
        
        # Check dimension compatibility
        if x_flat.shape != y_flat.shape:
            logger.error(f"Incompatible dimensions: {x_flat.shape} vs {y_flat.shape}")
            raise ValueError(f"Vectors must have the same dimensions, got {x_flat.shape} and {y_flat.shape}")
        
        # Compute L1 distance: sum of absolute differences
        distance_value = np.sum(np.abs(x_flat - y_flat))
        
        logger.debug(f"L1 distance computed: {distance_value}")
        return float(distance_value)
    
    def normalize(self, x: T) -> T:
        """
        Normalize a vector to have unit L1 norm.
        
        Parameters
        ----------
        x : T
            Vector to normalize
            
        Returns
        -------
        T
            Normalized vector with the same direction as x but unit L1 norm
            
        Raises
        ------
        ValueError
            If input is a zero vector or not a valid vector-like object
        TypeError
            If input type is not supported
        """
        logger.debug(f"Normalizing vector of type {type(x)} using L1 norm")
        
        # Convert input to numpy array if it's not already
        is_numpy = isinstance(x, np.ndarray)
        original_shape = None
        
        if not is_numpy:
            try:
                original_shape = np.array(x).shape
                x = np.array(x, dtype=float)
            except (ValueError, TypeError) as e:
                logger.error(f"Failed to convert input to numpy array: {e}")
                raise TypeError(f"Input must be convertible to numpy array: {e}")
        else:
            original_shape = x.shape
        
        # Ensure input is a vector
        if x.ndim > 2 or (x.ndim == 2 and min(x.shape) > 1):
            logger.error(f"Input has invalid shape: {x.shape}")
            raise ValueError(f"Input must be a vector, got shape {x.shape}")
        
        # Compute the L1 norm
        norm_value = self.compute(x)
        
        # Check for zero vector
        if norm_value == 0:
            logger.error("Cannot normalize a zero vector")
            raise ValueError("Cannot normalize a zero vector")
        
        # Normalize the vector
        normalized = x / norm_value
        
        # Return in the same format as the input
        if is_numpy:
            logger.debug("Returning normalized numpy array")
            return normalized
        else:
            # Convert back to the original type if possible
            try:
                # Try to convert back to the original type
                if isinstance(x, list):
                    logger.debug("Converting normalized vector back to list")
                    if x.ndim == 1:
                        return normalized.tolist()
                    else:
                        return [row.tolist() for row in normalized]
                elif isinstance(x, tuple):
                    logger.debug("Converting normalized vector back to tuple")
                    if x.ndim == 1:
                        return tuple(normalized.tolist())
                    else:
                        return tuple(tuple(row) for row in normalized.tolist())
                else:
                    logger.debug(f"Returning normalized vector as numpy array")
                    return normalized
            except Exception as e:
                logger.warning(f"Failed to convert normalized vector back to original type: {e}")
                return normalized
    
    def is_normalized(self, x: T, tolerance: float = 1e-10) -> bool:
        """
        Check if a vector has unit L1 norm within a given tolerance.
        
        Parameters
        ----------
        x : T
            Vector to check
        tolerance : float, optional
            Tolerance for floating-point comparison, by default 1e-10
            
        Returns
        -------
        bool
            True if the vector's L1 norm is within tolerance of 1.0, False otherwise
            
        Raises
        ------
        ValueError
            If input is not a valid vector-like object
        TypeError
            If input type is not supported
        """
        logger.debug(f"Checking if vector of type {type(x)} is normalized (L1 norm)")
        
        try:
            # Compute the L1 norm
            norm_value = self.compute(x)
            
            # Check if it's close to 1.0
            is_unit_norm = abs(norm_value - 1.0) <= tolerance
            
            logger.debug(f"Vector has L1 norm {norm_value}, is_normalized={is_unit_norm}")
            return is_unit_norm
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error checking if vector is normalized: {e}")
            raise
    
    def name(self) -> str:
        """
        Get the name of this norm implementation.
        
        Returns
        -------
        str
            String identifier for this norm
        """
        return "L1ManhattanNorm"