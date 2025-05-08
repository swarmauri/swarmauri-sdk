from typing import TypeVar, Sequence, Union, Literal, List, Any
import numpy as np
import logging
from pydantic import Field, validator

from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.ComponentBase import ComponentBase

# Type variable for generic implementation
T = TypeVar('T', bound=Union[Sequence, np.ndarray])

# Configure logger
logger = logging.getLogger(__name__)

@ComponentBase.register_type(MetricBase, "LpMetric")
class LpMetric(MetricBase):
    """
    Implementation of the Lp norm distance metric.
    
    The Lp metric (also known as Minkowski distance) is a generalization of 
    various distance metrics, including Euclidean (p=2), Manhattan (p=1), 
    and Chebyshev (p=∞) distances.
    
    For two vectors x and y, the Lp distance is defined as:
    d(x, y) = (∑|x_i - y_i|^p)^(1/p)
    
    Attributes
    ----------
    type : Literal["LpMetric"]
        Type identifier for the component
    p : float
        The order of the norm, must be greater than or equal to 1
    """
    type: Literal["LpMetric"] = "LpMetric"
    p: float = Field(default=2.0, description="The order of the norm (p ≥ 1)")
    
    @validator('p')
    def validate_p(cls, p_value):
        """
        Validate that p is at least 1.
        
        Parameters
        ----------
        p_value : float
            The p value to validate
            
        Returns
        -------
        float
            The validated p value
            
        Raises
        ------
        ValueError
            If p is less than 1
        """
        if p_value < 1:
            raise ValueError(f"p must be at least 1, got {p_value}")
        return p_value
    
    def distance(self, x: T, y: T) -> float:
        """
        Calculate the Lp distance between two vectors or sequences.
        
        Parameters
        ----------
        x : T
            First vector or sequence
        y : T
            Second vector or sequence
            
        Returns
        -------
        float
            The Lp distance between x and y
            
        Raises
        ------
        ValueError
            If x and y have different lengths
        TypeError
            If x and y cannot be converted to numpy arrays
        """
        try:
            # Convert inputs to numpy arrays for consistent handling
            x_array = np.asarray(x, dtype=float)
            y_array = np.asarray(y, dtype=float)
            
            # Check if dimensions match
            if x_array.shape != y_array.shape:
                msg = f"Input vectors must have the same shape: {x_array.shape} != {y_array.shape}"
                logger.error(msg)
                raise ValueError(msg)
            
            # Calculate the Lp distance
            if np.isinf(self.p):
                # Handle p = infinity (Chebyshev distance)
                distance = np.max(np.abs(x_array - y_array))
            else:
                # Regular Lp distance formula
                distance = np.sum(np.abs(x_array - y_array) ** self.p) ** (1.0 / self.p)
            
            return float(distance)
            
        except TypeError as e:
            logger.error(f"Cannot convert inputs to numpy arrays: {e}")
            raise TypeError(f"Inputs must be convertible to numpy arrays: {e}")
        except Exception as e:
            logger.error(f"Error calculating Lp distance: {e}")
            raise
    
    def are_identical(self, x: T, y: T) -> bool:
        """
        Check if two points are identical according to the Lp metric.
        
        Two points are considered identical if their distance is zero.
        
        Parameters
        ----------
        x : T
            First point
        y : T
            Second point
            
        Returns
        -------
        bool
            True if the points are identical (distance is zero), False otherwise
        """
        try:
            # Two points are identical if their distance is zero (or very close to zero)
            return np.isclose(self.distance(x, y), 0.0)
        except Exception as e:
            logger.error(f"Error checking identity: {e}")
            return False

    def __str__(self) -> str:
        """
        String representation of the LpMetric.
        
        Returns
        -------
        str
            A string describing the metric with its p value
        """
        if self.p == 1:
            name = "Manhattan"
        elif self.p == 2:
            name = "Euclidean"
        elif np.isinf(self.p):
            name = "Chebyshev"
        else:
            name = f"L{self.p}"
        
        return f"{name} Metric (p={self.p})"