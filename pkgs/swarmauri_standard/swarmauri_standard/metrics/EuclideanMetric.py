import logging
from typing import Union, Sequence, Tuple, Optional, Literal
from swarmauri_base.metrics import MetricBase
from swarmauri_standard.swarmauri_standard.norms import L2EuclideanNorm
import numpy as np

logger = logging.getLogger(__name__)

@ComponentBase.register_type(MetricBase, "EuclideanMetric")
class EuclideanMetric(MetricBase):
    """
    Provides a concrete implementation of the Euclidean (L2) distance metric.
    
    This class implements the MetricBase interface to compute the standard Euclidean 
    distance between vectors. The Euclidean distance is calculated as the square root 
    of the sum of the squared differences between corresponding elements of the vectors.
    
    Inherits From:
        MetricBase: The base class for all metric implementations.
    """
    
    type: Literal["EuclideanMetric"] = "EuclideanMetric"
    
    def __init__(self):
        """
        Initialize the EuclideanMetric instance.
        """
        super().__init__()
        
    def distance(self, x: Union[Sequence, np.ndarray, Tuple], y: Union[Sequence, np.ndarray, Tuple]) -> float:
        """
        Computes the Euclidean distance between two vectors x and y.
        
        Args:
            x: Union[Sequence, np.ndarray, Tuple]
                The first vector
            y: Union[Sequence, np.ndarray, Tuple]
                The second vector
                
        Returns:
            float: The Euclidean distance between x and y
        
        Raises:
            ValueError: If the input vectors are not of the same dimension
        """
        logger.debug(f"Computing Euclidean distance between vectors: {x} and {y}")
        
        # Ensure both vectors are numpy arrays for easier manipulation
        x_array = np.asarray(x)
        y_array = np.asarray(y)
        
        # Check if vectors have the same dimension
        if x_array.shape != y_array.shape:
            raise ValueError("Input vectors must have the same dimensions")
            
        # Compute the difference between vectors
        difference = x_array - y_array
        
        # Compute the sum of squares of the differences
        sum_squares = np.sum(difference ** 2)
        
        # Compute and return the square root of the sum of squares
        distance = np.sqrt(sum_squares)
        logger.debug(f"Computed Euclidean distance: {distance}")
        
        return distance
    
    def distances(self, x: Union[Sequence, np.ndarray, Tuple], 
                 ys: Optional[Union[Sequence, Tuple[Union[Sequence, np.ndarray, Tuple]]]] = None) -> Union[float, Sequence[float]]:
        """
        Computes the Euclidean distance(s) from vector x to one or more vectors y.
        
        Args:
            x: Union[Sequence, np.ndarray, Tuple]
                The reference vector
            ys: Optional[Union[Sequence, Tuple[Union[Sequence, np.ndarray, Tuple]]]] 
                Optional sequence of vectors to compute distances to
                
        Returns:
            Union[float, Sequence[float]]: 
                - float: If ys is None or contains one vector
                - Sequence[float]: If ys contains multiple vectors
                
        Raises:
            ValueError: If input vectors have mismatched dimensions
        """
        logger.debug(f"Computing Euclidean distances from vector: {x}")
        
        if ys is None or len(ys) == 1:
            # Compute single distance
            return self.distance(x, ys[0] if ys is not None else x)
        else:
            # Compute multiple distances
            distances = []
            for y in ys:
                distances.append(self.distance(x, y))
            return distances
            
    def check_non_negativity(self, x: Union[Sequence, np.ndarray, Tuple], y: Union[Sequence, np.ndarray, Tuple]) -> bool:
        """
        Checks if the non-negativity property holds: d(x, y) ≥ 0.
        
        Args:
            x: Union[Sequence, np.ndarray, Tuple]
                The first vector
            y: Union[Sequence, np.ndarray, Tuple]
                The second vector
                
        Returns:
            bool: True if the distance is non-negative, False otherwise
        """
        distance = self.distance(x, y)
        logger.debug(f"Checking non-negativity: {distance >= 0}")
        return distance >= 0
    
    def check_identity(self, x: Union[Sequence, np.ndarray, Tuple], y: Union[Sequence, np.ndarray, Tuple]) -> bool:
        """
        Checks the identity of indiscernibles property: d(x, y) = 0 if and only if x = y.
        
        Args:
            x: Union[Sequence, np.ndarray, Tuple]
                The first vector
            y: Union[Sequence, np.ndarray, Tuple]
                The second vector
                
        Returns:
            bool: True if d(x, y) = 0 implies x = y and vice versa, False otherwise
        """
        distance = self.distance(x, y)
        logger.debug(f"Checking identity: {distance == 0}")
        return distance == 0
    
    def check_symmetry(self, x: Union[Sequence, np.ndarray, Tuple], y: Union[Sequence, np.ndarray, Tuple]) -> bool:
        """
        Checks the symmetry property: d(x, y) = d(y, x).
        
        Args:
            x: Union[Sequence, np.ndarray, Tuple]
                The first vector
            y: Union[Sequence, np.ndarray, Tuple]
                The second vector
                
        Returns:
            bool: True if d(x, y) = d(y, x), False otherwise
        """
        d_xy = self.distance(x, y)
        d_yx = self.distance(y, x)
        logger.debug(f"Checking symmetry: {d_xy == d_yx}")
        return d_xy == d_yx
    
    def check_triangle_inequality(self, x: Union[Sequence, np.ndarray, Tuple], 
                                  y: Union[Sequence, np.ndarray, Tuple], 
                                  z: Union[Sequence, np.ndarray, Tuple]) -> bool:
        """
        Checks the triangle inequality property: d(x, z) ≤ d(x, y) + d(y, z).
        
        Args:
            x: Union[Sequence, np.ndarray, Tuple]
                The first vector
            y: Union[Sequence, np.ndarray, Tuple]
                The intermediate vector
            z: Union[Sequence, np.ndarray, Tuple]
                The third vector
                
        Returns:
            bool: True if d(x, z) ≤ d(x, y) + d(y, z), False otherwise
        """
        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)
        logger.debug(f"Checking triangle inequality: {d_xz <= d_xy + d_yz}")
        return d_xz <= d_xy + d_yz