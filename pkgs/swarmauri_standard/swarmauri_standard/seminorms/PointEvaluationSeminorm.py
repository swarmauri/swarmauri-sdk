import logging
from typing import Any, Optional, TypeVar, Literal, Callable, Dict, Union, Tuple, Generic
import numpy as np

from swarmauri_core.seminorms.ISeminorm import ISeminorm
from swarmauri_base.seminorms.SeminormBase import SeminormBase
from swarmauri_base.ComponentBase import ComponentBase

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for generic typing
T = TypeVar('T')

@ComponentBase.register_model()
class PointEvaluationSeminorm(SeminormBase, Generic[T]):
    """
    A seminorm that evaluates a function at a specific point.
    
    This class implements a seminorm that assigns a value based on the absolute value 
    of a function evaluated at a fixed coordinate or input point.
    
    Attributes
    ----------
    resource : Optional[str]
        The resource type identifier for this component.
    type : str
        The type identifier for this seminorm.
    point : Any
        The point at which to evaluate the function.
    """
    
    type: Literal["PointEvaluationSeminorm"] = "PointEvaluationSeminorm"
    point: Any
    
    def __init__(self, point: Any, **kwargs):
        """
        Initialize the PointEvaluationSeminorm with a specific evaluation point.
        
        Parameters
        ----------
        point : Any
            The point at which to evaluate functions.
        **kwargs : dict
            Additional keyword arguments to pass to the parent class.
        """
        super().__init__(**kwargs)
        self.point = point
        logger.debug(f"Initialized PointEvaluationSeminorm with point {point}")
    
    def evaluate(self, x: Callable[[Any], Union[float, complex]]) -> float:
        """
        Evaluate the seminorm for a given function.
        
        Computes the absolute value of the function evaluated at the specified point.
        
        Parameters
        ----------
        x : Callable[[Any], Union[float, complex]]
            The function to evaluate at the specified point.
            
        Returns
        -------
        float
            The absolute value of the function evaluated at the point.
            
        Raises
        ------
        ValueError
            If the function cannot be evaluated at the specified point.
        """
        logger.debug(f"Evaluating function at point {self.point}")
        try:
            result = x(self.point)
            # Handle complex numbers by taking the absolute value
            if isinstance(result, complex):
                return abs(result)
            return abs(float(result))
        except Exception as e:
            logger.error(f"Failed to evaluate function at point {self.point}: {str(e)}")
            raise ValueError(f"Function cannot be evaluated at the specified point: {str(e)}")
    
    def scale(self, x: Callable[[Any], Union[float, complex]], alpha: float) -> float:
        """
        Evaluate the seminorm of a scaled function.
        
        For a function f and scalar α, computes |α·f(point)|.
        
        Parameters
        ----------
        x : Callable[[Any], Union[float, complex]]
            The function to evaluate.
        alpha : float
            The scaling factor.
            
        Returns
        -------
        float
            The seminorm value of the scaled function.
        """
        logger.debug(f"Scaling function by {alpha} and evaluating at point {self.point}")
        # A scaled function can be evaluated directly using the scalar homogeneity property
        return abs(alpha) * self.evaluate(x)
    
    def triangle_inequality(self, x: Callable[[Any], Union[float, complex]], 
                            y: Callable[[Any], Union[float, complex]]) -> bool:
        """
        Verify that the triangle inequality holds for the given functions.
        
        Checks if |f(point) + g(point)| <= |f(point)| + |g(point)|.
        
        Parameters
        ----------
        x : Callable[[Any], Union[float, complex]]
            First function.
        y : Callable[[Any], Union[float, complex]]
            Second function.
            
        Returns
        -------
        bool
            True if the triangle inequality holds, False otherwise.
        """
        logger.debug(f"Checking triangle inequality for two functions at point {self.point}")
        
        # Define a function that represents the sum of x and y
        def sum_function(p):
            return x(p) + y(p)
        
        # Evaluate the seminorm of the sum
        sum_norm = self.evaluate(sum_function)
        
        # Evaluate the individual seminorms
        x_norm = self.evaluate(x)
        y_norm = self.evaluate(y)
        
        # Check if the triangle inequality holds
        return sum_norm <= x_norm + y_norm
    
    def is_zero(self, x: Callable[[Any], Union[float, complex]], tolerance: float = 1e-10) -> bool:
        """
        Check if the function evaluates to zero at the specified point (within a tolerance).
        
        Parameters
        ----------
        x : Callable[[Any], Union[float, complex]]
            The function to check.
        tolerance : float, optional
            The numerical tolerance for considering a value as zero.
            
        Returns
        -------
        bool
            True if the function value at the point is zero (within tolerance), False otherwise.
        """
        logger.debug(f"Checking if function is zero at point {self.point} with tolerance {tolerance}")
        return self.evaluate(x) < tolerance
    
    def is_definite(self) -> bool:
        """
        Check if this seminorm is actually a norm (i.e., it has the definiteness property).
        
        For a point evaluation seminorm, this is generally false, as different functions 
        can have the same value at a specific point but differ elsewhere.
        
        Returns
        -------
        bool
            False, as this seminorm is not definite.
        """
        logger.debug("Checking if PointEvaluationSeminorm is definite")
        # This seminorm is not definite because many different functions can have
        # a value of 0 at the specified point but be non-zero elsewhere
        return False