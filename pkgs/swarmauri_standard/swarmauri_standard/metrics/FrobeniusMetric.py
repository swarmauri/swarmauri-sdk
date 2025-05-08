from typing import Any, Literal, Optional, Union
import numpy as np
import logging
from pydantic import Field, validator

from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.ComponentBase import ComponentBase

# Configure logger
logger = logging.getLogger(__name__)

@ComponentBase.register_type(MetricBase, "FrobeniusMetric")
class FrobeniusMetric(MetricBase):
    """
    Frobenius metric for calculating distance between matrices.
    
    This metric computes the Frobenius norm of the difference between two matrices,
    which is the square root of the sum of the squares of all matrix elements.
    It's equivalent to treating the matrices as vectors and computing the Euclidean
    distance between them.
    """
    type: Literal["FrobeniusMetric"] = "FrobeniusMetric"
    
    @validator('type')
    def validate_type(cls, v):
        """
        Validate that the type field matches the expected value.
        
        Parameters
        ----------
        v : str
            The type value to validate
            
        Returns
        -------
        str
            The validated type value
            
        Raises
        ------
        ValueError
            If the type doesn't match "FrobeniusMetric"
        """
        if v != "FrobeniusMetric":
            raise ValueError(f"Type must be 'FrobeniusMetric', got '{v}'")
        return v
    
    def distance(self, x: Union[np.ndarray, list], y: Union[np.ndarray, list]) -> float:
        """
        Calculate the Frobenius distance between two matrices.
        
        Parameters
        ----------
        x : Union[np.ndarray, list]
            First matrix
        y : Union[np.ndarray, list]
            Second matrix
            
        Returns
        -------
        float
            The Frobenius distance between the matrices
            
        Raises
        ------
        ValueError
            If inputs are not arrays or have incompatible shapes
        TypeError
            If inputs cannot be converted to numpy arrays
        """
        try:
            # Convert inputs to numpy arrays if they're not already
            x_array = np.array(x, dtype=float)
            y_array = np.array(y, dtype=float)
            
            # Check if shapes match
            if x_array.shape != y_array.shape:
                error_msg = f"Matrix shapes must match. Got {x_array.shape} and {y_array.shape}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Calculate Frobenius norm of the difference
            # This is equivalent to sqrt(sum((x_ij - y_ij)^2))
            diff = x_array - y_array
            frobenius_distance = np.linalg.norm(diff, 'fro')
            
            logger.debug(f"Calculated Frobenius distance: {frobenius_distance}")
            return float(frobenius_distance)
            
        except TypeError as e:
            logger.error(f"Input conversion error: {str(e)}")
            raise TypeError(f"Inputs must be convertible to numpy arrays: {str(e)}")
        except Exception as e:
            logger.error(f"Error calculating Frobenius distance: {str(e)}")
            raise
    
    def are_identical(self, x: Union[np.ndarray, list], y: Union[np.ndarray, list]) -> bool:
        """
        Check if two matrices are identical according to the Frobenius metric.
        
        Parameters
        ----------
        x : Union[np.ndarray, list]
            First matrix
        y : Union[np.ndarray, list]
            Second matrix
            
        Returns
        -------
        bool
            True if the matrices are identical (distance is zero), False otherwise
        """
        try:
            # Use a small epsilon for floating-point comparison
            epsilon = 1e-10
            distance_value = self.distance(x, y)
            result = distance_value < epsilon
            
            logger.debug(f"Matrices identical check: {result} (distance={distance_value})")
            return result
            
        except Exception as e:
            logger.error(f"Error checking if matrices are identical: {str(e)}")
            raise
    
    def validate_inputs(self, x: Any, y: Any) -> tuple:
        """
        Validate that inputs are compatible with this metric.
        
        Parameters
        ----------
        x : Any
            First input to validate
        y : Any
            Second input to validate
            
        Returns
        -------
        tuple
            Tuple of validated numpy arrays
            
        Raises
        ------
        ValueError
            If inputs are not valid for this metric
        """
        try:
            # Convert inputs to numpy arrays
            x_array = np.array(x, dtype=float)
            y_array = np.array(y, dtype=float)
            
            # Ensure they're at least 2D
            if x_array.ndim < 1 or y_array.ndim < 1:
                raise ValueError("Inputs must be at least 1-dimensional")
            
            # Check shape compatibility
            if x_array.shape != y_array.shape:
                raise ValueError(f"Shapes must match. Got {x_array.shape} and {y_array.shape}")
                
            return x_array, y_array
            
        except Exception as e:
            logger.error(f"Input validation error: {str(e)}")
            raise ValueError(f"Invalid inputs for Frobenius metric: {str(e)}")