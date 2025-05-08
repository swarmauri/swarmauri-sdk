from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar('T')

class IMetric(ABC):
    """
    Interface for proper metric spaces.
    
    This abstract class defines the contract for metrics that satisfy the four
    fundamental axioms of metric spaces:
    1. Non-negativity: d(x,y) ≥ 0
    2. Point separation: d(x,y) = 0 if and only if x = y
    3. Symmetry: d(x,y) = d(y,x)
    4. Triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)
    
    Implementations of this interface must ensure all four axioms are satisfied
    for the metric to be mathematically valid.
    """
    
    @abstractmethod
    def distance(self, x: T, y: T) -> float:
        """
        Calculate the distance between two points in the metric space.
        
        Parameters
        ----------
        x : T
            First point
        y : T
            Second point
            
        Returns
        -------
        float
            The distance between x and y, which must be non-negative
            
        Notes
        -----
        Implementations must ensure this method satisfies all metric axioms:
        - Non-negativity: d(x,y) ≥ 0
        - Point separation: d(x,y) = 0 if and only if x = y
        - Symmetry: d(x,y) = d(y,x)
        - Triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)
        """
        pass
    
    @abstractmethod
    def are_identical(self, x: T, y: T) -> bool:
        """
        Check if two points are identical according to the metric.
        
        This is a convenience method that checks if the distance between
        two points is zero, which by the point separation axiom means 
        the points are identical.
        
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
        pass