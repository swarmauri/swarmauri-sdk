from abc import ABC, abstractmethod
from typing import Union, Callable, Sequence
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix
import logging

logger = logging.getLogger(__name__)


class IMetric(ABC):
    """
    Interface for metric spaces. This interface defines the contract for implementing
    different types of metrics, ensuring they satisfy the metric axioms:
    - Non-negativity: d(x, y) ≥ 0
    - Identity of indiscernibles: d(x, y) = 0 if and only if x = y
    - Symmetry: d(x, y) = d(y, x)
    - Triangle inequality: d(x, z) ≤ d(x, y) + d(y, z)
    
    All implementing classes must provide concrete implementations for the required methods
    while maintaining these properties for any input types supported.
    """
    
    @abstractmethod
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
        """
        raise NotImplementedError("distance method must be implemented")
    
    @abstractmethod
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
        """
        raise NotImplementedError("distances method must be implemented")
    
    @abstractmethod
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
        """
        raise NotImplementedError("check_non_negativity method must be implemented")
    
    @abstractmethod
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
        """
        raise NotImplementedError("check_identity method must be implemented")
    
    @abstractmethod
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
        """
        raise NotImplementedError("check_symmetry method must be implemented")
    
    @abstractmethod
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
        """
        raise NotImplementedError("check_triangle_inequality method must be implemented")
    
    def __init__(self):
        super().__init__()
        self._validate_implementation()
        
    def _validate_implementation(self):
        """
        Validates that all required methods are implemented in the subclass.
        This is called automatically during initialization.
        """
        logger.info("Validating IMetric implementation")
        required_methods = [
            "distance",
            "distances",
            "check_non_negativity",
            "check_identity",
            "check_symmetry",
            "check_triangle_inequality"
        ]
        
        for method_name in required_methods:
            method = getattr(self, method_name)
            if not callable(method) or isinstance(method, (classmethod, staticmethod)):
                raise NotImplementedError(f"Method {method_name} must be implemented in the subclass")