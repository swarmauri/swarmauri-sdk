from typing import Literal, Any, Union, Optional
import logging
import numpy as np

from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.ComponentBase import ComponentBase

# Configure logger
logger = logging.getLogger(__name__)

@ComponentBase.register_type(MetricBase, "AbsoluteValueMetric")
class AbsoluteValueMetric(MetricBase):
    """
    A metric for real numbers based on absolute value distance.
    
    This metric computes the distance between two scalar values using
    the absolute value of their difference: d(x,y) = |x - y|.
    
    This is the simplest valid metric for real numbers and satisfies all
    metric axioms:
    - Non-negativity: |x - y| ≥ 0
    - Point separation: |x - y| = 0 if and only if x = y
    - Symmetry: |x - y| = |y - x|
    - Triangle inequality: |x - z| ≤ |x - y| + |y - z|
    """
    type: Literal["AbsoluteValueMetric"] = "AbsoluteValueMetric"
    
    def distance(self, x: Union[int, float], y: Union[int, float]) -> float:
        """
        Calculate the absolute value distance between two scalar values.
        
        Parameters
        ----------
        x : Union[int, float]
            First scalar value
        y : Union[int, float]
            Second scalar value
            
        Returns
        -------
        float
            The absolute difference |x - y|
            
        Raises
        ------
        TypeError
            If inputs are not scalar values
        """
        # Validate inputs are scalar values
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            error_msg = f"AbsoluteValueMetric requires scalar inputs, got {type(x)} and {type(y)}"
            logger.error(error_msg)
            raise TypeError(error_msg)
        
        # Calculate absolute difference
        distance_value = abs(x - y)
        logger.debug(f"Calculated distance between {x} and {y}: {distance_value}")
        
        return distance_value
    
    def are_identical(self, x: Union[int, float], y: Union[int, float]) -> bool:
        """
        Check if two scalar values are identical (have zero distance).
        
        Parameters
        ----------
        x : Union[int, float]
            First scalar value
        y : Union[int, float]
            Second scalar value
            
        Returns
        -------
        bool
            True if the values are identical (x == y), False otherwise
            
        Raises
        ------
        TypeError
            If inputs are not scalar values
        """
        try:
            # For numerical stability, use a small epsilon value
            epsilon = 1e-10
            result = abs(self.distance(x, y)) < epsilon
            logger.debug(f"Identity check between {x} and {y}: {result}")
            return result
        except TypeError as e:
            # Re-raise the error from distance method
            raise e
    
    def validate_metric_axioms(self, x: Union[int, float], y: Union[int, float], z: Union[int, float]) -> bool:
        """
        Validate that the absolute value metric satisfies all four metric axioms.
        
        Parameters
        ----------
        x : Union[int, float]
            First test scalar value
        y : Union[int, float]
            Second test scalar value
        z : Union[int, float]
            Third test scalar value (for triangle inequality)
            
        Returns
        -------
        bool
            True if all axioms are satisfied, False otherwise
        """
        # The implementation from the base class is sufficient, as it uses our distance method
        return super().validate_metric_axioms(x, y, z)