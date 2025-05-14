from typing import TypeVar, Union, Callable, Sequence, Literal, List, Optional, Any, Dict, Tuple
import logging
import numpy as np
import math
from functools import lru_cache

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.pseudometrics.PseudometricBase import PseudometricBase
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

# Configure logging
logger = logging.getLogger(__name__)

# Type variables
T = TypeVar('T')

# Type aliases
VectorType = Union[IVector, List[float], Tuple[float, ...], np.ndarray]
MatrixType = Union[IMatrix, List[List[float]], np.ndarray]
InputType = Union[VectorType, MatrixType, Sequence[T], str, Callable]


@ComponentBase.register_type(PseudometricBase, "LpPseudometric")
class LpPseudometric(PseudometricBase):
    """
    Lp-style pseudometric without point separation.
    
    This class defines a pseudometric over function space using Lp integration,
    possibly on a subset of coordinates or domain. It allows for calculating
    distances between functions or vectors based on the Lp norm of their differences,
    but may not distinguish between all distinct inputs.
    
    Attributes
    ----------
    type : Literal["LpPseudometric"]
        Type identifier for this component
    p : float
        The parameter p for the Lp pseudometric (must be in [1, ∞])
    domain : Optional[Tuple[float, float]]
        The domain interval [a, b] to integrate over
    coordinates : Optional[List[int]]
        Specific coordinates to include in the distance calculation
    epsilon : float
        Small value used for numerical stability
    """
    
    type: Literal["LpPseudometric"] = "LpPseudometric"
    
    def __init__(
        self, 
        p: float = 2.0, 
        domain: Optional[Tuple[float, float]] = None,
        coordinates: Optional[List[int]] = None,
        epsilon: float = 1e-10
    ):
        """
        Initialize an Lp pseudometric.
        
        Parameters
        ----------
        p : float, optional
            The parameter p for the Lp pseudometric, by default 2.0
        domain : Optional[Tuple[float, float]], optional
            The domain interval [a, b] to integrate over, by default None
        coordinates : Optional[List[int]], optional
            Specific coordinates to include in the distance calculation, by default None
        epsilon : float, optional
            Small value used for numerical stability, by default 1e-10
            
        Raises
        ------
        ValueError
            If p is not in the range [1, ∞]
        ValueError
            If domain is specified but not a valid interval
        ValueError
            If coordinates contains negative indices
        """
        super().__init__()
        
        # Validate p parameter
        if p < 1:
            raise ValueError(f"Parameter p must be at least 1, got {p}")
        
        # Validate domain if provided
        if domain is not None:
            if len(domain) != 2 or domain[0] >= domain[1]:
                raise ValueError(f"Domain must be a valid interval [a, b] where a < b, got {domain}")
        
        # Validate coordinates if provided
        if coordinates is not None:
            if any(c < 0 for c in coordinates):
                raise ValueError("Coordinates must contain non-negative indices")
        
        self.p = p
        self.domain = domain
        self.coordinates = coordinates
        self.epsilon = epsilon
        
        logger.info(f"Initialized LpPseudometric with p={p}, domain={domain}, coordinates={coordinates}")
    
    def _convert_to_array(self, x: InputType) -> np.ndarray:
        """
        Convert input to a numpy array for computation.
        
        Parameters
        ----------
        x : InputType
            The input to convert
            
        Returns
        -------
        np.ndarray
            The converted input as a numpy array
            
        Raises
        ------
        TypeError
            If the input type is not supported
        """
        if isinstance(x, IVector):
            return np.array(x.to_array())
        elif isinstance(x, IMatrix):
            return np.array(x.to_array())
        elif isinstance(x, (list, tuple, np.ndarray)):
            return np.array(x, dtype=float)
        elif isinstance(x, str):
            # Convert string to array of character codes
            return np.array([ord(c) for c in x], dtype=float)
        elif callable(x):
            if self.domain is None:
                raise ValueError("Domain must be specified when using callable inputs")
            
            # Sample the function over the domain
            a, b = self.domain
            # Use 100 sample points by default
            sample_points = np.linspace(a, b, 100)
            return np.array([x(t) for t in sample_points], dtype=float)
        else:
            try:
                # Try to convert to array as a last resort
                return np.array(x, dtype=float)
            except:
                raise TypeError(f"Unsupported input type for LpPseudometric: {type(x)}")
    
    def _filter_coordinates(self, arr: np.ndarray) -> np.ndarray:
        """
        Filter array to include only specified coordinates.
        
        Parameters
        ----------
        arr : np.ndarray
            Input array
            
        Returns
        -------
        np.ndarray
            Filtered array containing only the specified coordinates
        """
        if self.coordinates is None:
            return arr
        
        if len(arr.shape) == 1:
            # For 1D arrays, select specific indices
            if max(self.coordinates) >= arr.shape[0]:
                raise ValueError(f"Coordinate index out of bounds: max index {max(self.coordinates)}, array shape {arr.shape}")
            return arr[self.coordinates]
        elif len(arr.shape) == 2:
            # For 2D arrays, select specific rows
            if max(self.coordinates) >= arr.shape[0]:
                raise ValueError(f"Coordinate index out of bounds: max index {max(self.coordinates)}, array shape {arr.shape}")
            return arr[self.coordinates, :]
        else:
            raise ValueError(f"Cannot filter coordinates for array with shape {arr.shape}")
    
    def distance(self, x: InputType, y: InputType) -> float:
        """
        Calculate the Lp pseudometric distance between two objects.
        
        Parameters
        ----------
        x : InputType
            The first object
        y : InputType
            The second object
            
        Returns
        -------
        float
            The Lp pseudometric distance between x and y
            
        Raises
        ------
        TypeError
            If inputs are of incompatible types
        ValueError
            If inputs have incompatible dimensions
        """
        logger.debug(f"Calculating Lp pseudometric distance with p={self.p} between inputs of types {type(x)} and {type(y)}")
        
        try:
            x_arr = self._convert_to_array(x)
            y_arr = self._convert_to_array(y)
            
            # Check if dimensions are compatible
            if x_arr.shape != y_arr.shape:
                raise ValueError(f"Inputs must have the same shape: {x_arr.shape} vs {y_arr.shape}")
            
            # Filter coordinates if specified
            if self.coordinates is not None:
                x_arr = self._filter_coordinates(x_arr)
                y_arr = self._filter_coordinates(y_arr)
            
            # Calculate the difference
            diff = np.abs(x_arr - y_arr)
            
            # Handle special cases for common p values
            if math.isclose(self.p, 1.0):
                return float(np.sum(diff))
            elif math.isclose(self.p, 2.0):
                return float(np.sqrt(np.sum(diff**2)))
            elif np.isinf(self.p):
                return float(np.max(diff))
            else:
                # General case for any p
                return float(np.sum(diff**self.p)**(1.0/self.p))
                
        except Exception as e:
            logger.error(f"Error calculating Lp pseudometric distance: {str(e)}")
            raise
    
    def distances(self, xs: Sequence[InputType], ys: Sequence[InputType]) -> List[List[float]]:
        """
        Calculate the pairwise distances between two collections of objects.
        
        Parameters
        ----------
        xs : Sequence[InputType]
            The first collection of objects
        ys : Sequence[InputType]
            The second collection of objects
            
        Returns
        -------
        List[List[float]]
            A matrix of distances where distances[i][j] is the distance between xs[i] and ys[j]
            
        Raises
        ------
        TypeError
            If inputs contain incompatible types
        ValueError
            If inputs have incompatible dimensions
        """
        logger.debug(f"Calculating pairwise Lp pseudometric distances between {len(xs)} and {len(ys)} objects")
        
        result = []
        for i, x in enumerate(xs):
            row = []
            for j, y in enumerate(ys):
                try:
                    row.append(self.distance(x, y))
                except Exception as e:
                    logger.error(f"Error calculating distance between xs[{i}] and ys[{j}]: {str(e)}")
                    raise
            result.append(row)
        
        return result
    
    def check_non_negativity(self, x: InputType, y: InputType) -> bool:
        """
        Check if the distance function satisfies the non-negativity property.
        
        Parameters
        ----------
        x : InputType
            The first object
        y : InputType
            The second object
            
        Returns
        -------
        bool
            True if d(x,y) ≥ 0, False otherwise
        """
        try:
            dist = self.distance(x, y)
            return dist >= 0
        except Exception as e:
            logger.error(f"Error checking non-negativity: {str(e)}")
            return False
    
    def check_symmetry(self, x: InputType, y: InputType, tolerance: float = 1e-10) -> bool:
        """
        Check if the distance function satisfies the symmetry property.
        
        Parameters
        ----------
        x : InputType
            The first object
        y : InputType
            The second object
        tolerance : float, optional
            The tolerance for floating-point comparisons, by default 1e-10
            
        Returns
        -------
        bool
            True if d(x,y) = d(y,x) within tolerance, False otherwise
        """
        try:
            dist_xy = self.distance(x, y)
            dist_yx = self.distance(y, x)
            return abs(dist_xy - dist_yx) <= tolerance
        except Exception as e:
            logger.error(f"Error checking symmetry: {str(e)}")
            return False
    
    def check_triangle_inequality(self, x: InputType, y: InputType, z: InputType, tolerance: float = 1e-10) -> bool:
        """
        Check if the distance function satisfies the triangle inequality.
        
        Parameters
        ----------
        x : InputType
            The first object
        y : InputType
            The second object
        z : InputType
            The third object
        tolerance : float, optional
            The tolerance for floating-point comparisons, by default 1e-10
            
        Returns
        -------
        bool
            True if d(x,z) ≤ d(x,y) + d(y,z) within tolerance, False otherwise
        """
        try:
            dist_xz = self.distance(x, z)
            dist_xy = self.distance(x, y)
            dist_yz = self.distance(y, z)
            
            # Account for floating-point errors with tolerance
            return dist_xz <= dist_xy + dist_yz + tolerance
        except Exception as e:
            logger.error(f"Error checking triangle inequality: {str(e)}")
            return False
    
    def check_weak_identity(self, x: InputType, y: InputType) -> bool:
        """
        Check if the distance function satisfies the weak identity property.
        
        In a pseudometric, d(x,y) = 0 is allowed even when x ≠ y.
        This method verifies that this property is properly handled.
        
        Parameters
        ----------
        x : InputType
            The first object
        y : InputType
            The second object
            
        Returns
        -------
        bool
            True if the pseudometric properly handles the weak identity property
        """
        # For Lp pseudometric, weak identity is satisfied when:
        # 1. d(x,x) = 0 for any x
        # 2. If objects differ only outside the measured domain/coordinates, d(x,y) = 0
        
        try:
            # Check if d(x,x) = 0
            if not math.isclose(self.distance(x, x), 0, abs_tol=self.epsilon):
                return False
            
            # Check if d(y,y) = 0
            if not math.isclose(self.distance(y, y), 0, abs_tol=self.epsilon):
                return False
            
            # If d(x,y) = 0, then the weak identity property is satisfied
            # for these particular x and y
            if math.isclose(self.distance(x, y), 0, abs_tol=self.epsilon):
                return True
            
            # If we're only measuring certain coordinates and the objects are
            # identical in those coordinates but different elsewhere, d(x,y) should be 0
            x_arr = self._convert_to_array(x)
            y_arr = self._convert_to_array(y)
            
            if self.coordinates is not None:
                x_filtered = self._filter_coordinates(x_arr)
                y_filtered = self._filter_coordinates(y_arr)
                
                # If the filtered arrays are equal but the original arrays are not,
                # then we have a case of weak identity
                return np.array_equal(x_filtered, y_filtered) and not np.array_equal(x_arr, y_arr)
            
            # If we have a domain restriction for callable functions,
            # we can't easily check this property in the general case
            
            return False
        except Exception as e:
            logger.error(f"Error checking weak identity: {str(e)}")
            return False
    
    def __str__(self) -> str:
        """
        Return a string representation of the LpPseudometric.
        
        Returns
        -------
        str
            String representation
        """
        domain_str = f", domain={self.domain}" if self.domain else ""
        coords_str = f", coordinates={self.coordinates}" if self.coordinates else ""
        return f"LpPseudometric(p={self.p}{domain_str}{coords_str})"
    
    def __repr__(self) -> str:
        """
        Return a detailed string representation of the LpPseudometric.
        
        Returns
        -------
        str
            Detailed string representation
        """
        return f"LpPseudometric(p={self.p}, domain={self.domain}, coordinates={self.coordinates}, epsilon={self.epsilon})"