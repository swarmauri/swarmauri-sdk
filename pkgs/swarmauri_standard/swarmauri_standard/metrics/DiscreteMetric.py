from typing import Union, Sequence, Optional
from abc import ABC
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_base.ComponentBase import ComponentBase
import logging

logger = logging.getLogger(__name__)

@ComponentBase.register_type(MetricBase, "DiscreteMetric")
class DiscreteMetric(MetricBase):
    """
    Provides a concrete implementation of a discrete metric space. The discrete metric 
    assigns distance 0 if two points are identical and distance 1 otherwise.
    
    Inherits from:
        MetricBase: Base class providing abstract methods for metric space implementations.
        
    Attributes:
        type: Literal["DiscreteMetric"] = "DiscreteMetric"
            Specifies the type identifier for this metric.
    """
    type: Literal["DiscreteMetric"] = "DiscreteMetric"
    
    def distance(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                 y: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Computes the discrete distance metric between two points x and y.
        
        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first point to compute distance from
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second point to compute distance to
        
        Returns:
            float: 0 if x and y are identical, 1 otherwise
        
        Raises:
            TypeError: If input types are not supported
        """
        if x == y:
            return 0.0
        else:
            return 1.0
    
    def distances(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                  ys: Union[Sequence[Union[IVector, IMatrix, Sequence, str, Callable]], None] = None) -> Union[float, Sequence[float]]:
        """
        Computes the discrete distances from point x to one or more points y.
        
        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The reference point
            ys: Union[Sequence[Union[IVector, IMatrix, Sequence, str, Callable]], None]
                Optional sequence of points to compute distances to
        
        Returns:
            Union[float, Sequence[float]]: Either a single distance or sequence of distances
        """
        if ys is None:
            return self.distance(x, ys)
        else:
            return [self.distance(x, y) for y in ys]
    
    def check_non_negativity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                             y: Union[IVector, IMatrix, Sequence, str, Callable]) -> bool:
        """
        Checks if the non-negativity property holds: d(x, y) ≥ 0.
        
        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first point
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second point
                
        Returns:
            bool: True if d(x, y) ≥ 0, False otherwise
        """
        return self.distance(x, y) >= 0
    
    def check_identity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                      y: Union[IVector, IMatrix, Sequence, str, Callable]) -> bool:
        """
        Checks the identity of indiscernibles property: d(x, y) = 0 if and only if x = y.
        
        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first point
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second point
                
        Returns:
            bool: True if d(x, y) = 0 implies x = y and vice versa, False otherwise
        """
        return self.distance(x, y) == 0 if x == y else True
    
    def check_symmetry(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                       y: Union[IVector, IMatrix, Sequence, str, Callable]) -> bool:
        """
        Checks the symmetry property: d(x, y) = d(y, x).
        
        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first point
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second point
                
        Returns:
            bool: True if d(x, y) = d(y, x), False otherwise
        """
        return self.distance(x, y) == self.distance(y, x)
    
    def check_triangle_inequality(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                                   y: Union[IVector, IMatrix, Sequence, str, Callable], 
                                   z: Union[IVector, IMatrix, Sequence, str, Callable]) -> bool:
        """
        Checks the triangle inequality property: d(x, z) ≤ d(x, y) + d(y, z).
        
        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first point
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The intermediate point
            z: Union[IVector, IMatrix, Sequence, str, Callable]
                The third point
                
        Returns:
            bool: True if d(x, z) ≤ d(x, y) + d(y, z), False otherwise
        """
        distance_xz = self.distance(x, z)
        distance_xy = self.distance(x, y)
        distance_yz = self.distance(y, z)
        return distance_xz <= (distance_xy + distance_yz)