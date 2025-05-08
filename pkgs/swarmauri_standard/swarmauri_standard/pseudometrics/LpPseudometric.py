from typing import Any, List, Optional, Union, TypeVar, Callable, Literal, Tuple
import logging
import numpy as np
from functools import partial
from swarmauri_base.pseudometrics.PseudometricBase import PseudometricBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)

T = TypeVar('T')

@ComponentBase.register_type(PseudometricBase, "LpPseudometric")
class LpPseudometric(PseudometricBase):
    """
    Lp-style pseudometric implementation without point separation.
    
    This class defines a pseudometric over function space using Lp integration,
    possibly on a subset of coordinates or domain. It allows measuring the 
    "distance" between functions, vectors, or other data types using various
    Lp norms (p=1 for Manhattan, p=2 for Euclidean, p=inf for Chebyshev).
    
    Attributes:
        type: Literal type identifier for this component
        p: The p-value for the Lp norm (1 ≤ p ≤ ∞)
        domain: Optional domain specification to restrict where the metric is applied
        coordinates: Optional list of coordinates to include in the calculation
        value_extractor: Function that extracts values from the input objects
    """
    
    type: Literal["LpPseudometric"] = "LpPseudometric"
    
    def __init__(
        self, 
        p: Union[int, float, str] = 2, 
        domain: Optional[Union[Tuple, List, np.ndarray]] = None,
        coordinates: Optional[List[Union[int, str]]] = None,
        value_extractor: Optional[Callable[[T], Union[List, np.ndarray]]] = None,
        **kwargs
    ):
        """
        Initialize the Lp pseudometric.
        
        Args:
            p: The p-value for the Lp norm (1 ≤ p ≤ ∞)
            domain: Optional domain specification to restrict where the metric is applied
            coordinates: Optional list of coordinates to include in the calculation
            value_extractor: Function that extracts values from the input objects
            **kwargs: Additional keyword arguments to pass to parent classes
        
        Raises:
            ValueError: If p is not in the valid range [1, ∞]
        """
        super().__init__(**kwargs)
        
        # Handle p parameter
        if p == 'inf' or p == '∞' or p == float('inf'):
            self.p = float('inf')
        else:
            self.p = float(p)
            
        # Validate p parameter
        if self.p < 1:
            logger.error(f"Invalid p value: {p}. Must be at least 1.")
            raise ValueError(f"Parameter p must be at least 1, got {p}")
        
        self.domain = domain
        self.coordinates = coordinates
        
        # Set default value extractor if none provided
        if value_extractor is None:
            self.value_extractor = lambda x: x
        else:
            self.value_extractor = value_extractor
            
        logger.debug(f"Initialized {self.__class__.__name__} with p={self.p}")
    
    def _extract_and_prepare(self, x: T) -> np.ndarray:
        """
        Extract values from input and prepare them for distance calculation.
        
        Args:
            x: Input data
            
        Returns:
            Prepared numpy array with values
        """
        values = self.value_extractor(x)
        
        # Convert to numpy array if not already
        if not isinstance(values, np.ndarray):
            values = np.array(values, dtype=float)
            
        # Apply coordinate filtering if specified
        if self.coordinates is not None:
            values = values[self.coordinates]
            
        # Apply domain filtering if specified
        if self.domain is not None:
            if isinstance(self.domain, (list, tuple)) and len(self.domain) == 2:
                # Assuming domain is [min, max] range
                mask = (values >= self.domain[0]) & (values <= self.domain[1])
                values = values[mask]
                
        return values
    
    def distance(self, x: T, y: T) -> float:
        """
        Calculate the Lp pseudometric distance between two points.
        
        Args:
            x: First point
            y: Second point
            
        Returns:
            The Lp distance between the points
        """
        x_values = self._extract_and_prepare(x)
        y_values = self._extract_and_prepare(y)
        
        # Ensure the arrays have the same shape
        if x_values.shape != y_values.shape:
            # If shapes differ, we only consider the intersection of domains
            min_len = min(len(x_values), len(y_values))
            x_values = x_values[:min_len]
            y_values = y_values[:min_len]
            logger.warning(f"Inputs have different shapes. Using first {min_len} elements.")
        
        # Calculate the Lp distance
        if self.p == float('inf'):
            # L-infinity norm (maximum absolute difference)
            distance = float(np.max(np.abs(x_values - y_values)))
        else:
            # General Lp norm
            distance = float(np.sum(np.abs(x_values - y_values) ** self.p) ** (1 / self.p))
        
        # Validate the non-negativity property
        self._validate_non_negativity(distance, x, y)
        
        return distance
    
    def batch_distance(self, xs: List[T], ys: List[T]) -> List[float]:
        """
        Calculate distances between corresponding pairs of points from two lists.
        
        Args:
            xs: List of first points
            ys: List of second points
            
        Returns:
            List of distances between corresponding points
            
        Raises:
            ValueError: If input lists have different lengths
        """
        if len(xs) != len(ys):
            logger.error(f"Input lists have different lengths: {len(xs)} vs {len(ys)}")
            raise ValueError("Input lists must have the same length")
        
        return [self.distance(x, y) for x, y in zip(xs, ys)]
    
    def pairwise_distances(self, points: List[T]) -> List[List[float]]:
        """
        Calculate all pairwise distances between points in the given list.
        
        Args:
            points: List of points
            
        Returns:
            A square matrix (as list of lists) where element [i][j] 
            contains the distance between points[i] and points[j]
        """
        n = len(points)
        distances = [[0.0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(i+1, n):
                dist = self.distance(points[i], points[j])
                # Exploit symmetry to reduce computations
                distances[i][j] = dist
                distances[j][i] = dist
                
        return distances
    
    def verify_properties(self, samples: List[T]) -> bool:
        """
        Verify that the pseudometric satisfies the required mathematical properties.
        
        Args:
            samples: List of sample points to use for verification
            
        Returns:
            True if all properties are satisfied, raises exception otherwise
        """
        if len(samples) < 3:
            logger.warning("Need at least 3 samples to verify all properties")
            return False
            
        # Test sample points
        x, y, z = samples[0], samples[1], samples[2]
        
        # Test non-negativity
        d_xy = self.distance(x, y)
        self._validate_non_negativity(d_xy, x, y)
        
        # Test symmetry
        d_yx = self.distance(y, x)
        self._validate_symmetry(d_xy, d_yx, x, y)
        
        # Test triangle inequality
        d_xz = self.distance(x, z)
        d_yz = self.distance(y, z)
        self._validate_triangle_inequality(d_xz, d_xy, d_yz, x, y, z)
        
        logger.info("All pseudometric properties successfully verified")
        return True
    
    def __str__(self) -> str:
        """
        Return a string representation of the pseudometric.
        
        Returns:
            String description of the pseudometric
        """
        domain_str = f", domain={self.domain}" if self.domain else ""
        coords_str = f", coordinates={self.coordinates}" if self.coordinates else ""
        return f"LpPseudometric(p={self.p}{domain_str}{coords_str})"