from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union
import logging
import numpy as np
from pydantic import Field, validator

from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.ComponentBase import ComponentBase

# Configure logger
logger = logging.getLogger(__name__)

@ComponentBase.register_type(MetricBase, "SobolevMetric")
class SobolevMetric(MetricBase):
    """
    Metric derived from the Sobolev norm, accounting for both function values and derivatives.
    
    The Sobolev metric measures the distance between functions by considering both
    their values and the smoothness of their variations through derivatives.
    This is particularly useful for comparing functions where the rate of change
    is as important as the actual values.
    
    Attributes
    ----------
    type : Literal["SobolevMetric"]
        Type identifier for the metric
    weights : Dict[int, float]
        Weights for each derivative order. Key 0 represents the function value itself.
    norm_type : int
        The order of the norm to use (1 for L1, 2 for L2, etc.)
    """
    type: Literal["SobolevMetric"] = "SobolevMetric"
    weights: Dict[int, float] = Field(
        default_factory=lambda: {0: 1.0, 1: 0.5},
        description="Weights for each derivative order (0 = function value)"
    )
    norm_type: int = Field(
        default=2,
        description="Order of the norm (1 for L1, 2 for L2, etc.)",
        ge=1
    )
    
    @validator('weights')
    def validate_weights(cls, weights):
        """
        Validate that weights dictionary contains at least the zero-order term
        and that all weights are non-negative.
        
        Parameters
        ----------
        weights : Dict[int, float]
            Dictionary of weights for each derivative order
            
        Returns
        -------
        Dict[int, float]
            Validated weights dictionary
            
        Raises
        ------
        ValueError
            If weights dictionary is invalid
        """
        if 0 not in weights:
            raise ValueError("Weights must include at least the zero-order term (key 0)")
        
        for order, weight in weights.items():
            if weight < 0:
                raise ValueError(f"Weight for order {order} must be non-negative")
            
        return weights
    
    def distance(self, x: Any, y: Any) -> float:
        """
        Calculate the Sobolev distance between two functions or arrays.
        
        Parameters
        ----------
        x : Any
            First function or array. Should support derivatives if weights include higher orders.
        y : Any
            Second function or array. Should support derivatives if weights include higher orders.
            
        Returns
        -------
        float
            The Sobolev distance between x and y
            
        Notes
        -----
        If x and y are functions, they should have a 'derivative' method or attribute 
        that returns the derivative of the specified order.
        If x and y are arrays, they should represent function values at sample points,
        and finite differences will be used to approximate derivatives.
        """
        try:
            # Calculate the weighted sum of norms of function and its derivatives
            total_distance = 0.0
            
            for order, weight in self.weights.items():
                if weight == 0:
                    continue  # Skip terms with zero weight
                
                # Get the appropriate derivative or function value
                x_deriv = self._get_derivative(x, order)
                y_deriv = self._get_derivative(y, order)
                
                # Calculate the norm of the difference
                diff = self._compute_difference(x_deriv, y_deriv)
                norm_diff = self._compute_norm(diff)
                
                # Add the weighted norm to the total distance
                total_distance += weight * norm_diff
            
            return total_distance
            
        except Exception as e:
            logger.error(f"Error calculating Sobolev distance: {str(e)}")
            raise ValueError(f"Failed to calculate Sobolev distance: {str(e)}")
    
    def are_identical(self, x: Any, y: Any) -> bool:
        """
        Check if two functions are identical according to the Sobolev metric.
        
        Parameters
        ----------
        x : Any
            First function or array
        y : Any
            Second function or array
            
        Returns
        -------
        bool
            True if the functions are identical (distance is zero), False otherwise
        """
        try:
            # Two functions are identical if their Sobolev distance is zero
            distance_value = self.distance(x, y)
            return abs(distance_value) < 1e-10  # Using epsilon for float comparison
        except Exception as e:
            logger.error(f"Error checking if functions are identical: {str(e)}")
            return False
    
    def _get_derivative(self, func: Any, order: int) -> Any:
        """
        Get the derivative of the specified order from a function or array.
        
        Parameters
        ----------
        func : Any
            Function or array
        order : int
            Order of the derivative
            
        Returns
        -------
        Any
            The derivative of the specified order
            
        Notes
        -----
        This method handles different input types:
        - If func is a callable with a 'derivative' method, it uses that
        - If func is a numpy array, it uses finite differences
        - If func is a dictionary with derivatives, it looks for the right key
        """
        if order == 0:
            return func  # Return the function itself for order 0
        
        # Case 1: Function object with a derivative method
        if hasattr(func, 'derivative') and callable(getattr(func, 'derivative')):
            return func.derivative(order)
        
        # Case 2: Function object with derivatives as attributes
        derivative_attr = f"derivative_{order}"
        if hasattr(func, derivative_attr):
            return getattr(func, derivative_attr)
        
        # Case 3: Dictionary with derivatives as keys
        if isinstance(func, dict) and order in func:
            return func[order]
        
        # Case 4: Numpy array - use finite differences
        if isinstance(func, np.ndarray):
            return self._compute_finite_difference(func, order)
        
        # Case 5: If func is callable, try to evaluate it on a grid and compute derivatives
        if callable(func):
            try:
                # Create a simple grid for evaluation
                x = np.linspace(0, 1, 100)
                values = np.array([func(xi) for xi in x])
                return self._compute_finite_difference(values, order)
            except Exception as e:
                logger.error(f"Failed to compute derivative for callable: {str(e)}")
        
        raise ValueError(f"Cannot compute derivative of order {order} for the given input type")
    
    def _compute_finite_difference(self, values: np.ndarray, order: int) -> np.ndarray:
        """
        Compute finite difference approximation of derivatives.
        
        Parameters
        ----------
        values : np.ndarray
            Array of function values
        order : int
            Order of the derivative
            
        Returns
        -------
        np.ndarray
            Array of derivative values
        """
        # Simple implementation using numpy's diff function
        result = values.copy()
        for _ in range(order):
            result = np.diff(result, n=1, axis=0)
            # Pad the result to maintain the same size
            if len(result) < len(values):
                result = np.pad(result, (0, 1), mode='edge')
        
        return result
    
    def _compute_difference(self, x: Any, y: Any) -> np.ndarray:
        """
        Compute the difference between two functions or arrays.
        
        Parameters
        ----------
        x : Any
            First function or array
        y : Any
            Second function or array
            
        Returns
        -------
        np.ndarray
            The difference between x and y
        """
        # Handle different input types
        if isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
            # Ensure the arrays have the same shape
            if x.shape != y.shape:
                raise ValueError(f"Arrays must have the same shape: {x.shape} vs {y.shape}")
            return x - y
        
        # If both are callable, evaluate them on a grid
        if callable(x) and callable(y):
            grid = np.linspace(0, 1, 100)  # Default grid
            x_values = np.array([x(t) for t in grid])
            y_values = np.array([y(t) for t in grid])
            return x_values - y_values
        
        # Try direct subtraction for other types
        try:
            return x - y
        except Exception as e:
            logger.error(f"Failed to compute difference: {str(e)}")
            raise ValueError(f"Cannot compute difference for the given input types")
    
    def _compute_norm(self, values: np.ndarray) -> float:
        """
        Compute the norm of the given values.
        
        Parameters
        ----------
        values : np.ndarray
            Array of values
            
        Returns
        -------
        float
            The norm of the values
        """
        # Handle different norm types
        if self.norm_type == 1:
            return np.sum(np.abs(values))
        elif self.norm_type == 2:
            return np.sqrt(np.sum(np.square(values)))
        else:
            return np.power(np.sum(np.power(np.abs(values), self.norm_type)), 1.0/self.norm_type)