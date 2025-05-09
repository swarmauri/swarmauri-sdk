from typing import Union, Sequence, Any, Optional, Callable, Literal, Tuple
import logging
from abc import ABC

from swarmauri_base.metrics import MetricBase
from swarmauri_core.vectors import IVector
from swarmauri_core.matrices import IMatrix

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "LpMetric")
class LpMetric(MetricBase):
    """Concrete implementation of the Lp metric for p in (1, ∞)."""

    type: Literal["LpMetric"] = "LpMetric"
    
    def __init__(self, p: float = 2):
        """
        Initialize the LpMetric instance with parameter p.
        
        Args:
            p: The parameter of the Lp metric. Must be greater than 1 and finite.
        """
        super().__init__()
        if p <= 1 or not self._is_finite(p):
            raise ValueError("Parameter p must be greater than 1 and finite.")
        self.p = p
        
    def _is_finite(self, value: float) -> bool:
        """
        Check if the given value is finite.
        
        Args:
            value: The value to check.
            
        Returns:
            bool: True if the value is finite, False otherwise.
        """
        return value == value and value != float('inf') and value != float('-inf')
        
    def distance(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Compute the Lp distance between two points x and y.
        
        Args:
            x: The first point to compute distance from
            y: The second point to compute distance to
            
        Returns:
            float: The computed Lp distance between x and y
        """
        logger.debug(f"Computing Lp distance between {x} and {y}")
        
        # Convert x and y to vectors if they're not already
        if not isinstance(x, IVector):
            x = self._convert_to_vector(x)
        if not isinstance(y, IVector):
            y = self._convert_to_vector(y)
            
        # Compute element-wise difference
        difference = x - y
        
        # Compute the Lp norm of the difference
        return self._compute_norm(difference)
        
    def _convert_to_vector(self, obj: Union[IMatrix, Sequence, str, Callable]) -> IVector:
        """
        Convert various input types to a vector representation.
        
        Args:
            obj: The input object to convert
            
        Returns:
            IVector: The vector representation of the input object
        """
        if isinstance(obj, IMatrix):
            if obj.is_row_vector:
                return obj.rows[0]
            else:
                # For column vectors, stack rows into a single vector
                return sum(obj.rows, [])
        elif isinstance(obj, Sequence):
            return IVector(obj)
        elif isinstance(obj, str):
            return IVector([ord(c) for c in obj])
        elif callable(obj):
            result = obj()
            return IVector([result]) if not isinstance(result, (int, float)) else IVector([float(result)])
        else:
            raise TypeError(f"Unsupported type for conversion: {type(obj)}")
            
    def _compute_norm(self, vector: IVector) -> float:
        """
        Compute the Lp norm of a vector.
        
        Args:
            vector: The vector to compute the norm for
            
        Returns:
            float: The computed Lp norm
        """
        if self.p == 1:
            return sum(abs(x) for x in vector)
        elif self.p == 2:
            return (sum(x**2 for x in vector)) ** 0.5
        else:
            return (sum(abs(x)**self.p for x in vector)) ** (1.0 / self.p)
        
    def check_non_negativity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable]) -> bool:
        """
        Check if the non-negativity property holds: d(x, y) ≥ 0.
        
        Args:
            x: The first point
            y: The second point
            
        Returns:
            bool: True if d(x, y) ≥ 0, False otherwise
        """
        logger.debug("Checking non-negativity property")
        distance = self.distance(x, y)
        return distance >= 0
        
    def check_identity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable]) -> bool:
        """
        Check the identity of indiscernibles property: d(x, y) = 0 if and only if x = y.
        
        Args:
            x: The first point
            y: The second point
            
        Returns:
            bool: True if d(x, y) = 0 implies x = y and vice versa, False otherwise
        """
        logger.debug("Checking identity property")
        return self.distance(x, y) == 0
        
    def check_symmetry(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable]) -> bool:
        """
        Check the symmetry property: d(x, y) = d(y, x).
        
        Args:
            x: The first point
            y: The second point
            
        Returns:
            bool: True if d(x, y) = d(y, x), False otherwise
        """
        logger.debug("Checking symmetry property")
        return self.distance(x, y) == self.distance(y, x)
        
    def check_triangle_inequality(self, x: Union[IVector, IMatrix, Sequence, str, Callable], y: Union[IVector, IMatrix, Sequence, str, Callable], z: Union[IVector, IMatrix, Sequence, str, Callable]) -> bool:
        """
        Check the triangle inequality property: d(x, z) ≤ d(x, y) + d(y, z).
        
        Args:
            x: The first point
            y: The intermediate point
            z: The third point
            
        Returns:
            bool: True if d(x, z) ≤ d(x, y) + d(y, z), False otherwise
        """
        logger.debug("Checking triangle inequality property")
        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)
        return d_xz <= d_xy + d_yz
        
    def __str__(self) -> str:
        return f"LpMetric(p={self.p})"
    
    def __repr__(self) -> str:
        return f"LpMetric(p={self.p})"