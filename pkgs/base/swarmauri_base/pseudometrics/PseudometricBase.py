from typing import Any, TypeVar, Generic, List, Optional
import logging
from abc import ABC
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.pseudometrics.IPseudometric import IPseudometric

T = TypeVar('T')

logger = logging.getLogger(__name__)

@ComponentBase.register_model()
class PseudometricBase(IPseudometric[T], ComponentBase, ABC):
    """
    Abstract base class implementing pseudometric behavior.
    
    This class provides a foundation for pseudometric distance functions that satisfy
    non-negativity, symmetry, and triangle inequality, but without the separation property.
    
    A pseudometric allows d(x,y) = 0 for x ≠ y, which means distinct points may have
    zero distance between them.
    
    Properties:
    - Non-negativity: d(x,y) ≥ 0
    - Symmetry: d(x,y) = d(y,x)
    - Triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)
    """
    
    resource: Optional[str] = ResourceTypes.PSEUDOMETRIC.value
    
    def __init__(self, **kwargs):
        """
        Initialize the pseudometric base class.
        
        Args:
            **kwargs: Additional keyword arguments to pass to parent classes
        """
        super().__init__(**kwargs)
        logger.debug(f"Initialized {self.__class__.__name__}")
    
    def distance(self, x: T, y: T) -> float:
        """
        Calculate the pseudometric distance between two points.
        
        Args:
            x: First point
            y: Second point
            
        Returns:
            The non-negative distance value between the points
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
            
        Note:
            Implementation must ensure:
            - Return value is non-negative
            - d(x,y) equals d(y,x) (symmetry)
            - d(x,z) is ≤ d(x,y) + d(y,z) (triangle inequality)
        """
        raise NotImplementedError("Subclasses must implement the distance method")
    
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
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement the batch_distance method")
    
    def pairwise_distances(self, points: List[T]) -> List[List[float]]:
        """
        Calculate all pairwise distances between points in the given list.
        
        Args:
            points: List of points
            
        Returns:
            A square matrix (as list of lists) where element [i][j] 
            contains the distance between points[i] and points[j]
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement the pairwise_distances method")
    
    def _validate_non_negativity(self, distance: float, x: T, y: T) -> None:
        """
        Validate that the distance satisfies the non-negativity property.
        
        Args:
            distance: The calculated distance
            x: First point
            y: Second point
            
        Raises:
            ValueError: If the distance is negative
        """
        if distance < 0:
            logger.error(f"Non-negativity violation: d({x},{y}) = {distance} < 0")
            raise ValueError(f"Pseudometric violation: distance must be non-negative, got {distance}")
    
    def _validate_symmetry(self, distance_xy: float, distance_yx: float, x: T, y: T) -> None:
        """
        Validate that the distances satisfy the symmetry property.
        
        Args:
            distance_xy: Distance from x to y
            distance_yx: Distance from y to x
            x: First point
            y: Second point
            
        Raises:
            ValueError: If the distances are not equal
        """
        # Using a small epsilon for floating point comparison
        epsilon = 1e-10
        if abs(distance_xy - distance_yx) > epsilon:
            logger.error(f"Symmetry violation: d({x},{y}) = {distance_xy} ≠ d({y},{x}) = {distance_yx}")
            raise ValueError(f"Pseudometric violation: symmetry property not satisfied")
    
    def _validate_triangle_inequality(self, distance_xz: float, distance_xy: float, 
                                     distance_yz: float, x: T, y: T, z: T) -> None:
        """
        Validate that the distances satisfy the triangle inequality property.
        
        Args:
            distance_xz: Distance from x to z
            distance_xy: Distance from x to y
            distance_yz: Distance from y to z
            x: First point
            y: Second point
            z: Third point
            
        Raises:
            ValueError: If the triangle inequality is violated
        """
        # Using a small epsilon for floating point comparison
        epsilon = 1e-10
        if distance_xz > distance_xy + distance_yz + epsilon:
            logger.error(f"Triangle inequality violation: d({x},{z}) = {distance_xz} > "
                         f"d({x},{y}) + d({y},{z}) = {distance_xy} + {distance_yz} = {distance_xy + distance_yz}")
            raise ValueError(f"Pseudometric violation: triangle inequality not satisfied")