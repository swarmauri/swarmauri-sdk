from typing import Optional, TypeVar, Any
import logging
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.metrics.IMetric import IMetric

# Type variable for generic implementation
T = TypeVar('T')

# Configure logger
logger = logging.getLogger(__name__)

@ComponentBase.register_model()
class MetricBase(IMetric, ComponentBase):
    """
    Base implementation for metric spaces.
    
    This class provides a foundation for implementing proper metric spaces
    that satisfy the four fundamental metric axioms:
    1. Non-negativity: d(x,y) ≥ 0
    2. Point separation: d(x,y) = 0 if and only if x = y
    3. Symmetry: d(x,y) = d(y,x)
    4. Triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)
    
    Concrete implementations must override the distance method
    to provide the actual distance calculation logic.
    """
    resource: Optional[str] = Field(default=ResourceTypes.METRIC.value)
    
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
        
        Raises
        ------
        NotImplementedError
            This base method must be overridden by concrete implementations
        """
        logger.error("distance method must be implemented by concrete subclasses")
        raise NotImplementedError("The distance method must be implemented by concrete subclasses")
    
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
            
        Raises
        ------
        NotImplementedError
            This base method must be overridden by concrete implementations
        """
        logger.error("are_identical method must be implemented by concrete subclasses")
        raise NotImplementedError("The are_identical method must be implemented by concrete subclasses")
    
    def validate_metric_axioms(self, x: T, y: T, z: T) -> bool:
        """
        Validate that the implemented metric satisfies all four metric axioms.
        
        Parameters
        ----------
        x : T
            First test point
        y : T
            Second test point
        z : T
            Third test point (for triangle inequality)
            
        Returns
        -------
        bool
            True if all axioms are satisfied, False otherwise
            
        Notes
        -----
        This is a utility method to help implementations verify their
        correctness. It checks:
        1. Non-negativity: d(x,y) ≥ 0
        2. Point separation: d(x,x) = 0
        3. Symmetry: d(x,y) = d(y,x)
        4. Triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)
        """
        try:
            # Check non-negativity
            d_xy = self.distance(x, y)
            if d_xy < 0:
                logger.warning(f"Non-negativity axiom violated: d({x},{y}) = {d_xy} < 0")
                return False
            
            # Check identity of indiscernibles (point separation)
            d_xx = self.distance(x, x)
            if d_xx != 0:
                logger.warning(f"Point separation axiom violated: d({x},{x}) = {d_xx} ≠ 0")
                return False
            
            # Check symmetry
            d_yx = self.distance(y, x)
            if abs(d_xy - d_yx) > 1e-10:  # Using epsilon for float comparison
                logger.warning(f"Symmetry axiom violated: d({x},{y}) = {d_xy} ≠ d({y},{x}) = {d_yx}")
                return False
            
            # Check triangle inequality
            d_xz = self.distance(x, z)
            d_yz = self.distance(y, z)
            if d_xz > d_xy + d_yz + 1e-10:  # Using epsilon for float comparison
                logger.warning(f"Triangle inequality violated: d({x},{z}) = {d_xz} > d({x},{y}) + d({y},{z}) = {d_xy + d_yz}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating metric axioms: {str(e)}")
            return False