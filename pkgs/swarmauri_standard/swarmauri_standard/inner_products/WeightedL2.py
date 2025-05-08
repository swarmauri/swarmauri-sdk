import logging
from typing import Any, Callable, Dict, Literal, Optional, Union, TypeVar
import numpy as np
from numpy.typing import NDArray

from swarmauri_core.inner_products.IInnerProduct import T
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from swarmauri_core.ComponentBase import ComponentBase

@ComponentBase.register_type(InnerProductBase, "WeightedL2")
class WeightedL2(InnerProductBase):
    """
    Weighted L2 inner product implementation for real/complex functions.
    
    This class implements a position-dependent weighted L2 inner product for 
    function spaces. The inner product is defined as:
    <f, g> = ∫ w(x) f(x) g*(x) dx
    where w(x) is a strictly positive weight function and g* is the complex conjugate of g.
    
    Attributes
    ----------
    type : Literal["WeightedL2"]
        The type identifier for this inner product
    weight_function : Callable[[NDArray], NDArray]
        The weight function w(x) used in the inner product calculation
    integration_domain : Optional[Dict[str, Any]]
        Domain specification for the integration
    integration_method : str
        Method used for numerical integration
    """
    
    type: Literal["WeightedL2"] = "WeightedL2"
    weight_function: Callable[[NDArray], NDArray]
    integration_domain: Optional[Dict[str, Any]] = None
    integration_method: str = "trapezoidal"
    
    def __init__(
        self, 
        weight_function: Callable[[NDArray], NDArray],
        integration_domain: Optional[Dict[str, Any]] = None,
        integration_method: str = "trapezoidal"
    ) -> None:
        """
        Initialize the WeightedL2 inner product.
        
        Parameters
        ----------
        weight_function : Callable[[NDArray], NDArray]
            A function that takes position coordinates and returns positive weights.
            Must be strictly positive everywhere in the domain.
        integration_domain : Optional[Dict[str, Any]], optional
            Domain specification for the integration, by default None
        integration_method : str, optional
            Method used for numerical integration, by default "trapezoidal"
            
        Raises
        ------
        ValueError
            If the weight function is not callable
        """
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Initializing WeightedL2 inner product")
        
        if not callable(weight_function):
            self.logger.error("Weight function must be callable")
            raise ValueError("Weight function must be callable")
        
        self.weight_function = weight_function
        self.integration_domain = integration_domain
        self.integration_method = integration_method
        
        self.logger.debug(f"Inner product initialized with integration method: {integration_method}")
    
    def compute(self, vec1: T, vec2: T) -> float:
        """
        Compute the weighted L2 inner product between two functions.
        
        The inner product is computed as the integral of weight(x) * vec1(x) * conj(vec2(x))
        over the specified domain.
        
        Parameters
        ----------
        vec1 : T
            First function in the inner product
        vec2 : T
            Second function in the inner product
            
        Returns
        -------
        float
            The resulting inner product value
            
        Raises
        ------
        ValueError
            If the vectors are incompatible for inner product calculation
        TypeError
            If the vectors are of unsupported types
        """
        self.logger.debug("Computing weighted L2 inner product")
        
        if not self.is_compatible(vec1, vec2):
            self.logger.error("Incompatible vectors for inner product calculation")
            raise ValueError("Vectors must be compatible for inner product calculation")
        
        try:
            # Handle different possible input types
            if hasattr(vec1, 'grid') and hasattr(vec2, 'grid'):
                # Case for discretized functions with grid attribute
                grid = vec1.grid
                values1 = vec1.values
                values2 = vec2.values
                
                # Calculate weights at grid points
                weights = self.weight_function(grid)
                
                # Check for non-positive weights
                if np.any(weights <= 0):
                    self.logger.error("Weight function must be strictly positive")
                    raise ValueError("Weight function must be strictly positive")
                
                # Compute the weighted inner product based on integration method
                if self.integration_method == "trapezoidal":
                    # For multidimensional grids, we need the grid spacing
                    if hasattr(grid, 'dx'):
                        dx = grid.dx
                    else:
                        # Default to 1.0 if not specified
                        dx = 1.0
                    
                    # Compute the inner product using trapezoidal rule
                    integrand = weights * values1 * np.conjugate(values2)
                    result = np.trapz(integrand) * dx
                    
                elif self.integration_method == "simpson":
                    # Implementation for Simpson's rule
                    if hasattr(grid, 'dx'):
                        dx = grid.dx
                    else:
                        dx = 1.0
                    
                    integrand = weights * values1 * np.conjugate(values2)
                    result = np.sum(integrand) * dx
                else:
                    self.logger.error(f"Unsupported integration method: {self.integration_method}")
                    raise ValueError(f"Unsupported integration method: {self.integration_method}")
                
            elif isinstance(vec1, np.ndarray) and isinstance(vec2, np.ndarray):
                # Case for raw numpy arrays (assuming uniform grid)
                if not hasattr(self, '_grid'):
                    # Create a default grid if not provided
                    self.logger.warning("No grid provided for array inputs, using default grid")
                    n_points = len(vec1)
                    self._grid = np.linspace(0, 1, n_points)
                
                weights = self.weight_function(self._grid)
                
                # Check for non-positive weights
                if np.any(weights <= 0):
                    self.logger.error("Weight function must be strictly positive")
                    raise ValueError("Weight function must be strictly positive")
                
                # Compute the inner product
                integrand = weights * vec1 * np.conjugate(vec2)
                dx = self._grid[1] - self._grid[0]  # Assuming uniform grid
                result = np.trapz(integrand, dx=dx)
                
            else:
                self.logger.error("Unsupported vector types for inner product calculation")
                raise TypeError("Unsupported vector types for inner product calculation")
            
            # Return real part if the result is real (within numerical precision)
            if np.isclose(result.imag, 0):
                return float(result.real)
            return complex(result)
            
        except Exception as e:
            self.logger.error(f"Error computing inner product: {str(e)}")
            raise
    
    def is_compatible(self, vec1: T, vec2: T) -> bool:
        """
        Check if two vectors are compatible for weighted L2 inner product calculation.
        
        Parameters
        ----------
        vec1 : T
            First vector to check
        vec2 : T
            Second vector to check
            
        Returns
        -------
        bool
            True if the vectors are compatible, False otherwise
        """
        self.logger.debug("Checking compatibility for weighted L2 inner product")
        
        # Both inputs should be of the same type
        if type(vec1) != type(vec2):
            self.logger.debug("Vectors are of different types")
            return False
        
        try:
            # Check for discretized functions with grid attribute
            if hasattr(vec1, 'grid') and hasattr(vec2, 'grid'):
                # Grids must be the same
                if not np.array_equal(vec1.grid, vec2.grid):
                    self.logger.debug("Grids are not equal")
                    return False
                
                # Values must have the same shape
                if vec1.values.shape != vec2.values.shape:
                    self.logger.debug("Value arrays have different shapes")
                    return False
                
                return True
                
            # Check for numpy arrays
            elif isinstance(vec1, np.ndarray) and isinstance(vec2, np.ndarray):
                # Arrays must have the same shape
                if vec1.shape != vec2.shape:
                    self.logger.debug("Arrays have different shapes")
                    return False
                
                return True
                
            else:
                self.logger.debug("Unsupported vector types")
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking compatibility: {str(e)}")
            return False
    
    def validate_weight_function(self, grid: NDArray) -> bool:
        """
        Validate that the weight function is strictly positive on the given grid.
        
        Parameters
        ----------
        grid : NDArray
            The grid points to check the weight function on
            
        Returns
        -------
        bool
            True if the weight function is valid (strictly positive), False otherwise
        """
        try:
            weights = self.weight_function(grid)
            return np.all(weights > 0)
        except Exception as e:
            self.logger.error(f"Error validating weight function: {str(e)}")
            return False