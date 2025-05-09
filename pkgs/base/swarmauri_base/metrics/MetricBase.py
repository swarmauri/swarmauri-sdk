from typing import Union, Sequence, Optional
from abc import ABC
from swarmauri_core.metrics.IMetric import IMetric
from swarmauri_base.ComponentBase import ComponentBase
import logging

logger = logging.getLogger(__name__)

@ComponentBase.register_model()
class MetricBase(IMetric, ComponentBase):
    """
    Provides a base implementation for metric spaces. This class implements the IMetric interface
    with abstract methods that must be implemented by subclasses to provide concrete distance calculations.
    """
    
    resource: Optional[str] = "metric"
    
    def distance(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Computes the distance metric between two points x and y.
        
        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first point to compute distance from
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second point to compute distance to
        
        Returns:
            float: The computed distance metric between x and y
        
        Raises:
            NotImplementedError: This method must be implemented in a subclass
        """
        raise NotImplementedError("distance method must be implemented in a subclass")
    
    def distances(self, x: Union[IVector, IMatrix, Sequence, str, Callable], ys: Union[Sequence[Union[IVector, IMatrix, Sequence, str, Callable]], None] = None) -> Union[float, Sequence[float]]:
        """
        Computes the distance metric(s) from point x to one or more points y.
        
        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The reference point
            ys: Union[Sequence[Union[IVector, IMatrix, Sequence, str, Callable]], None]
                Optional sequence of points to compute distances to
        
        Returns:
            Union[float, Sequence[float]]: Either a single distance or sequence of distances
        
        Raises:
            NotImplementedError: This method must be implemented in a subclass
        """
        raise NotImplementedError("distances method must be implemented in a subclass")
    
    def check_non_negativity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable]) -> bool:
        """
        Checks if the non-negativity property holds: d(x, y) ≥ 0.
        
        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first point
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second point
                
        Returns:
            bool: True if d(x, y) ≥ 0, False otherwise
        
        Raises:
            NotImplementedError: This method must be implemented in a subclass
        """
        raise NotImplementedError("check_non_negativity method must be implemented in a subclass")
    
    def check_identity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable]) -> bool:
        """
        Checks the identity of indiscernibles property: d(x, y) = 0 if and only if x = y.
        
        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first point
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second point
                
        Returns:
            bool: True if d(x, y) = 0 implies x = y and vice versa, False otherwise
        
        Raises:
            NotImplementedError: This method must be implemented in a subclass
        """
        raise NotImplementedError("check_identity method must be implemented in a subclass")
    
    def check_symmetry(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable]) -> bool:
        """
        Checks the symmetry property: d(x, y) = d(y, x).
        
        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first point
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second point
                
        Returns:
            bool: True if d(x, y) = d(y, x), False otherwise
        
        Raises:
            NotImplementedError: This method must be implemented in a subclass
        """
        raise NotImplementedError("check_symmetry method must be implemented in a subclass")
    
    def check_triangle_inequality(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable], z: Union[IVector, IMatrix, Sequence, str, Callable]) -> bool:
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
        
        Raises:
            NotImplementedError: This method must be implemented in a subclass
        """
        raise NotImplementedError("check_triangle_inequality method must be implemented in a subclass")