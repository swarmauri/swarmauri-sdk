from typing import Union, Sequence
from swarmauri_base.metrics import MetricBase
from swarmauri_base.ComponentBase import ComponentBase
import logging

logger = logging.getLogger(__name__)

@ComponentBase.register_type(MetricBase, "HammingMetric")
class HammingMetric(MetricBase):
    """
    Provides a concrete implementation of a metric space that computes the Hamming distance.
    The Hamming distance between two sequences of equal length is the number of positions
    at which the corresponding symbols are different. This implementation is suitable for
    binary data, bitwise data, and categorical vectors.
    """
    
    type: str = "HammingMetric"
    
    def distance(self, x: Union[Sequence, str, bytes], y: Union[Sequence, str, bytes]) -> float:
        """
        Computes the Hamming distance between two sequences of equal length.
        
        Args:
            x: Union[Sequence, str, bytes]
                The first sequence
            y: Union[Sequence, str, bytes]
                The second sequence
                
        Returns:
            float: The Hamming distance between x and y
        
        Raises:
            ValueError: If the input sequences are not of the same length
        """
        if len(x) != len(y):
            logger.error("Input sequences must be of the same length for Hamming distance calculation")
            raise ValueError("Input sequences must be of the same length")
            
        mismatch_count = 0
        for x_elem, y_elem in zip(x, y):
            if x_elem != y_elem:
                mismatch_count += 1
                
        logger.debug(f"Calculated Hamming distance: {mismatch_count}")
        return float(mismatch_count)
    
    def check_non_negativity(self, x: Union[Sequence, str, bytes], y: Union[Sequence, str, bytes]) -> bool:
        """
        Checks if the non-negativity property holds: d(x, y) ≥ 0.
        
        Args:
            x: Union[Sequence, str, bytes]
                The first sequence
            y: Union[Sequence, str, bytes]
                The second sequence
                
        Returns:
            bool: True if d(x, y) ≥ 0, False otherwise
        """
        distance = self.distance(x, y)
        non_negative = distance >= 0
        logger.debug(f"Non-negativity check result: {non_negative}")
        return non_negative
    
    def check_identity(self, x: Union[Sequence, str, bytes], y: Union[Sequence, str, bytes]) -> bool:
        """
        Checks the identity of indiscernibles property: d(x, y) = 0 if and only if x = y.
        
        Args:
            x: Union[Sequence, str, bytes]
                The first sequence
            y: Union[Sequence, str, bytes]
                The second sequence
                
        Returns:
            bool: True if d(x, y) = 0 implies x = y and vice versa, False otherwise
        """
        distance = self.distance(x, y)
        identity_holds = (distance == 0) == (x == y)
        logger.debug(f"Identity check result: {identity_holds}")
        return identity_holds
    
    def check_symmetry(self, x: Union[Sequence, str, bytes], y: Union[Sequence, str, bytes]) -> bool:
        """
        Checks the symmetry property: d(x, y) = d(y, x).
        
        Args:
            x: Union[Sequence, str, bytes]
                The first sequence
            y: Union[Sequence, str, bytes]
                The second sequence
                
        Returns:
            bool: True if d(x, y) = d(y, x), False otherwise
        """
        distance_xy = self.distance(x, y)
        distance_yx = self.distance(y, x)
        symmetric = distance_xy == distance_yx
        logger.debug(f"Symmetry check result: {symmetric}")
        return symmetric
    
    def check_triangle_inequality(self, x: Union[Sequence, str, bytes], y: Union[Sequence, str, bytes], z: Union[Sequence, str, bytes]) -> bool:
        """
        Checks the triangle inequality property: d(x, z) ≤ d(x, y) + d(y, z).
        
        Args:
            x: Union[Sequence, str, bytes]
                The first sequence
            y: Union[Sequence, str, bytes]
                The second sequence
            z: Union[Sequence, str, bytes]
                The third sequence
                
        Returns:
            bool: True if d(x, z) ≤ d(x, y) + d(y, z), False otherwise
        """
        distance_xz = self.distance(x, z)
        distance_xy = self.distance(x, y)
        distance_yz = self.distance(y, z)
        triangle_inequality_holds = distance_xz <= distance_xy + distance_yz
        logger.debug(f"Triangle inequality check result: {triangle_inequality_holds}")
        return triangle_inequality_holds