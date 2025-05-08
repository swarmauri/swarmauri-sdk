from typing import TypeVar, Any, Literal, Hashable
import logging

from pydantic import Field
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.ComponentBase import ComponentBase

# Type variable for generic implementation
T = TypeVar('T', bound=Hashable)

# Configure logger
logger = logging.getLogger(__name__)

@ComponentBase.register_type(MetricBase, "DiscreteMetric")
class DiscreteMetric(MetricBase):
    """
    Discrete metric implementation.
    
    This metric defines distance as:
    - 0 if two elements are equal
    - 1 if two elements are different
    
    This is a valid metric space that satisfies all four metric axioms.
    Works with any hashable types.
    """
    type: Literal["DiscreteMetric"] = "DiscreteMetric"
    
    def distance(self, x: T, y: T) -> float:
        """
        Calculate the discrete distance between two points.
        
        Parameters
        ----------
        x : T
            First point (any hashable type)
        y : T
            Second point (any hashable type)
            
        Returns
        -------
        float
            0.0 if x equals y, 1.0 otherwise
        """
        try:
            # The discrete metric returns 0 if points are equal, 1 otherwise
            return 0.0 if x == y else 1.0
        except Exception as e:
            logger.error(f"Error calculating discrete distance between {x} and {y}: {str(e)}")
            # Re-raise the exception to maintain transparent error handling
            raise
    
    def are_identical(self, x: T, y: T) -> bool:
        """
        Check if two points are identical according to the discrete metric.
        
        Parameters
        ----------
        x : T
            First point (any hashable type)
        y : T
            Second point (any hashable type)
            
        Returns
        -------
        bool
            True if x equals y, False otherwise
        """
        try:
            # Points are identical if they are equal
            return x == y
        except Exception as e:
            logger.error(f"Error checking identity between {x} and {y}: {str(e)}")
            # Re-raise the exception to maintain transparent error handling
            raise