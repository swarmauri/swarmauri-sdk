from typing import List, Union, Literal, TypeVar, Any
import numpy as np
import logging
from pydantic import Field, validator

from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.ComponentBase import ComponentBase

# Configure logger
logger = logging.getLogger(__name__)

# Type variable for generic implementation
T = TypeVar('T')

@ComponentBase.register_type(MetricBase, "EuclideanMetric")
class EuclideanMetric(MetricBase):
    """
    Euclidean distance metric implementation.
    
    This class implements the standard Euclidean (L2) distance between vectors.
    It satisfies all four metric axioms:
    1. Non-negativity: d(x,y) ≥ 0
    2. Point separation: d(x,y) = 0 if and only if x = y
    3. Symmetry: d(x,y) = d(y,x)
    4. Triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)
    
    The Euclidean distance is calculated as the square root of the sum of squared differences
    between corresponding elements of the input vectors.
    """
    type: Literal["EuclideanMetric"] = "EuclideanMetric"
    
    def distance(self, x: Union[List[float], np.ndarray], y: Union[List[float], np.ndarray]) -> float:
        """
        Calculate the Euclidean (L2) distance between two vectors.
        
        Parameters
        ----------
        x : Union[List[float], np.ndarray]
            First vector
        y : Union[List[float], np.ndarray]
            Second vector
            
        Returns
        -------
        float
            The Euclidean distance between x and y
            
        Raises
        ------
        ValueError
            If input vectors have different dimensions
        TypeError
            If inputs are not valid vector types
        """
        try:
            # Convert inputs to numpy arrays if they aren't already
            x_array = np.array(x, dtype=float)
            y_array = np.array(y, dtype=float)
            
            # Check if dimensions match
            if x_array.shape != y_array.shape:
                error_msg = f"Input vectors must have the same dimensions. Got {x_array.shape} and {y_array.shape}."
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Calculate Euclidean distance
            # L2 norm of the difference between vectors
            distance = np.linalg.norm(x_array - y_array)
            
            return float(distance)
            
        except TypeError as e:
            logger.error(f"Invalid input types: {str(e)}")
            raise TypeError(f"Input vectors must be numeric arrays or lists. Error: {str(e)}")
        except Exception as e:
            logger.error(f"Error calculating Euclidean distance: {str(e)}")
            raise
    
    def are_identical(self, x: Union[List[float], np.ndarray], y: Union[List[float], np.ndarray]) -> bool:
        """
        Check if two vectors are identical according to the Euclidean metric.
        
        Two vectors are considered identical if their Euclidean distance is zero
        (or very close to zero, accounting for floating-point precision).
        
        Parameters
        ----------
        x : Union[List[float], np.ndarray]
            First vector
        y : Union[List[float], np.ndarray]
            Second vector
            
        Returns
        -------
        bool
            True if the vectors are identical (distance is effectively zero), False otherwise
        """
        try:
            # Use a small epsilon value to account for floating-point precision
            epsilon = 1e-10
            return self.distance(x, y) < epsilon
        except Exception as e:
            logger.error(f"Error checking vector identity: {str(e)}")
            return False
    
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
            If the type value is not "EuclideanMetric"
        """
        if v != "EuclideanMetric":
            raise ValueError(f"Type must be 'EuclideanMetric', got '{v}'")
        return v