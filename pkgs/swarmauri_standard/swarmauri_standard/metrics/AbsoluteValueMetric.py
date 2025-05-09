import logging
from typing import Union, Any
from abc import ABC
from swarmauri_base.metrics import MetricBase
from swarmauri_core.metrics import IMetric

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "AbsoluteValueMetric")
class AbsoluteValueMetric(MetricBase):
    """
    Provides a concrete implementation of the MetricBase class for absolute value distance metric.
    
    This class implements the distance, distances, and various property checking methods
    required for a valid metric space. The distance is computed as the absolute difference
    between two scalar values.
    """
    
    type: str = "AbsoluteValueMetric"
    
    def __init__(self):
        """
        Initializes the AbsoluteValueMetric instance.
        """
        super().__init__()
        self._type = self.type
        
    def distance(self, x: Union[float, int], y: Union[float, int]) -> float:
        """
        Computes the absolute distance between two scalar values.
        
        Args:
            x: Union[float, int]
                The first scalar value
            y: Union[float, int]
                The second scalar value
                
        Returns:
            float: The absolute difference between x and y
        """
        logger.debug("Computing absolute distance between %s and %s", x, y)
        return abs(x - y)
    
    def distances(self, x: Union[float, int], ys: Union[Sequence[Union[float, int]], None] = None) -> Union[float, Sequence[float]]:
        """
        Computes the absolute distances from a reference point to one or more points.
        
        Args:
            x: Union[float, int]
                The reference point
            ys: Union[Sequence[Union[float, int]], None]
                Optional sequence of points to compute distances to
                
        Returns:
            Union[float, Sequence[float]]: Either a single distance or sequence of distances
        """
        logger.debug("Computing absolute distances from %s to %s", x, ys)
        if ys is None:
            return self.distance(x, ys)
        return [self.distance(x, y) for y in ys]
    
    def check_non_negativity(self, x: Union[float, int], y: Union[float, int]) -> bool:
        """
        Checks if the non-negativity property holds: d(x, y) ≥ 0.
        
        Args:
            x: Union[float, int]
                The first point
            y: Union[float, int]
                The second point
                
        Returns:
            bool: True if d(x, y) ≥ 0, False otherwise
        """
        logger.debug("Checking non-negativity for points %s and %s", x, y)
        distance = self.distance(x, y)
        return distance >= 0
    
    def check_identity(self, x: Union[float, int], y: Union[float, int]) -> bool:
        """
        Checks the identity of indiscernibles property: d(x, y) = 0 if and only if x = y.
        
        Args:
            x: Union[float, int]
                The first point
            y: Union[float, int]
                The second point
                
        Returns:
            bool: True if d(x, y) = 0 implies x = y and vice versa, False otherwise
        """
        logger.debug("Checking identity for points %s and %s", x, y)
        return x == y if self.distance(x, y) == 0 else False
    
    def check_symmetry(self, x: Union[float, int], y: Union[float, int]) -> bool:
        """
        Checks the symmetry property: d(x, y) = d(y, x).
        
        Args:
            x: Union[float, int]
                The first point
            y: Union[float, int]
                The second point
                
        Returns:
            bool: True if d(x, y) = d(y, x), False otherwise
        """
        logger.debug("Checking symmetry for points %s and %s", x, y)
        return self.distance(x, y) == self.distance(y, x)
    
    def check_triangle_inequality(self, x: Union[float, int], y: Union[float, int], z: Union[float, int]) -> bool:
        """
        Checks the triangle inequality property: d(x, z) ≤ d(x, y) + d(y, z).
        
        Args:
            x: Union[float, int]
                The first point
            y: Union[float, int]
                The intermediate point
            z: Union[float, int]
                The third point
                
        Returns:
            bool: True if d(x, z) ≤ d(x, y) + d(y, z), False otherwise
        """
        logger.debug("Checking triangle inequality for points %s, %s, and %s", x, y, z)
        return self.distance(x, z) <= self.distance(x, y) + self.distance(y, z)