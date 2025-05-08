from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic

T = TypeVar('T')

class IPseudometric(Generic[T], ABC):
    """
    Interface for pseudometric distance functions.
    
    A pseudometric is a distance function that satisfies non-negativity,
    symmetry, and triangle inequality, but may not distinguish distinct points.
    
    Unlike a metric, a pseudometric allows d(x,y) = 0 for x ≠ y, which means
    distinct points may have zero distance between them.
    
    Requirements:
    - Non-negativity: d(x,y) ≥ 0
    - Symmetry: d(x,y) = d(y,x)
    - Triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)
    """
    
    @abstractmethod
    def distance(self, x: T, y: T) -> float:
        """
        Calculate the pseudometric distance between two points.
        
        Args:
            x: First point
            y: Second point
            
        Returns:
            The non-negative distance value between the points
            
        Note:
            This method must satisfy the pseudometric properties:
            - Return value must be non-negative
            - d(x,y) must equal d(y,x) (symmetry)
            - d(x,z) must be ≤ d(x,y) + d(y,z) (triangle inequality)
            - May return 0 even if x ≠ y
        """
        pass
    
    @abstractmethod
    def batch_distance(self, xs: list[T], ys: list[T]) -> list[float]:
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
        pass
    
    @abstractmethod
    def pairwise_distances(self, points: list[T]) -> list[list[float]]:
        """
        Calculate all pairwise distances between points in the given list.
        
        Args:
            points: List of points
            
        Returns:
            A square matrix (as list of lists) where element [i][j] 
            contains the distance between points[i] and points[j]
        """
        pass