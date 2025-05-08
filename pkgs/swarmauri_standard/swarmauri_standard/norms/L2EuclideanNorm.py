import logging
import numpy as np
from typing import Any, List, Optional, Tuple, Union, Literal, TypeVar, Generic
import math
from pydantic import Field

from swarmauri_base.norms.NormBase import NormBase, T
from swarmauri_base.ComponentBase import ComponentBase

# Configure logging
logger = logging.getLogger(__name__)

@ComponentBase.register_type(NormBase, "L2EuclideanNorm")
class L2EuclideanNorm(NormBase):
    """
    Implementation of the Euclidean (L2) norm.
    
    This class computes the Euclidean norm for real-valued vectors,
    which is the square root of the sum of squares of vector components.
    
    Attributes
    ----------
    type : Literal["L2EuclideanNorm"]
        Type identifier for this norm implementation
    resource : str
        Resource type identifier, inherited from NormBase
    """
    type: Literal["L2EuclideanNorm"] = "L2EuclideanNorm"
    
    def compute(self, x: T) -> float:
        """
        Compute the Euclidean (L2) norm of a vector.
        
        Parameters
        ----------
        x : T
            Vector-like object whose norm is to be calculated
            
        Returns
        -------
        float
            The Euclidean norm value
            
        Raises
        ------
        ValueError
            If input is not a valid vector-like object
        TypeError
            If input type is not supported
        """
        try:
            # Convert input to numpy array for consistent handling
            x_array = np.asarray(x, dtype=float)
            
            # Calculate the L2 norm: sqrt(sum(x_i^2))
            norm_value = math.sqrt(np.sum(np.square(x_array)))
            
            logger.debug(f"Computed L2 norm: {norm_value}")
            return norm_value
        except TypeError as e:
            logger.error(f"Type error when computing L2 norm: {e}")
            raise TypeError(f"Input must be convertible to a numeric array: {e}")
        except ValueError as e:
            logger.error(f"Value error when computing L2 norm: {e}")
            raise ValueError(f"Invalid input for L2 norm computation: {e}")
    
    def distance(self, x: T, y: T) -> float:
        """
        Compute the Euclidean distance between two vectors.
        
        Parameters
        ----------
        x : T
            First vector
        y : T
            Second vector
            
        Returns
        -------
        float
            The Euclidean distance between x and y
            
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
            
            # Check if dimensions are compatible
            if x_array.shape != y_array.shape:
                raise ValueError(f"Incompatible dimensions: {x_array.shape} and {y_array.shape}")
            
            # Calculate the Euclidean distance: ||x - y||_2
            difference = x_array - y_array
            distance_value = self.compute(difference)
            
            logger.debug(f"Computed Euclidean distance: {distance_value}")
            return distance_value
        except TypeError as e:
            logger.error(f"Type error when computing Euclidean distance: {e}")
            raise TypeError(f"Inputs must be convertible to numeric arrays: {e}")
        except ValueError as e:
            logger.error(f"Value error when computing Euclidean distance: {e}")
            raise ValueError(f"Invalid inputs for Euclidean distance computation: {e}")
    
    def normalize(self, x: T) -> T:
        """
        Normalize a vector to have unit Euclidean norm.
        
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
        try:
            # Convert input to numpy array
            x_array = np.asarray(x, dtype=float)
            
            # Compute the norm
            norm_value = self.compute(x_array)
            
            # Check for zero vector
            if norm_value < 1e-15:  # Using a small epsilon to account for floating-point precision
                logger.warning("Attempted to normalize a zero or near-zero vector")
                raise ValueError("Cannot normalize a zero vector")
            
            # Normalize the vector
            normalized = x_array / norm_value
            
            # Return the same type as the input if possible
            if isinstance(x, np.ndarray):
                result = normalized
            elif isinstance(x, list):
                result = normalized.tolist()
            else:
                # Try to convert back to the original type
                try:
                    result = type(x)(normalized)
                except:
                    result = normalized
            
            logger.debug(f"Normalized vector with L2 norm")
            return result
        except TypeError as e:
            logger.error(f"Type error when normalizing vector: {e}")
            raise TypeError(f"Input must be convertible to a numeric array: {e}")
        except ValueError as e:
            logger.error(f"Value error when normalizing vector: {e}")
            raise ValueError(f"Invalid input for normalization: {e}")
    
    def is_normalized(self, x: T, tolerance: float = 1e-10) -> bool:
        """
        Check if a vector has unit Euclidean norm within a given tolerance.
        
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
        try:
            # Compute the norm
            norm_value = self.compute(x)
            
            # Check if the norm is within tolerance of 1.0
            is_unit_norm = abs(norm_value - 1.0) <= tolerance
            
            logger.debug(f"Vector normalization check: norm={norm_value}, is_normalized={is_unit_norm}")
            return is_unit_norm
        except TypeError as e:
            logger.error(f"Type error when checking normalization: {e}")
            raise TypeError(f"Input must be convertible to a numeric array: {e}")
        except ValueError as e:
            logger.error(f"Value error when checking normalization: {e}")
            raise ValueError(f"Invalid input for normalization check: {e}")
    
    def name(self) -> str:
        """
        Get the name of this norm implementation.
        
        Returns
        -------
        str
            String identifier for this norm
        """
        return "L2EuclideanNorm"