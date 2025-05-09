import logging
import numpy as np
from typing import Union, Sequence, Optional, Any
from swarmauri_base.ComponentBase import ComponentBase
from base.swarmauri_base.metrics.MetricBase import MetricBase

logger = logging.getLogger(__name__)

@ComponentBase.register_type(MetricBase, "SupremumMetric")
class SupremumMetric(MetricBase):
    """
    Provides a concrete implementation of the L∞ metric (supremum metric) for 
    vector spaces. The L∞ metric defines the distance between two vectors as 
    the maximum absolute difference between their corresponding components.

    This class implements the MetricBase interface and provides functionality 
    for computing distances between vectors in a bounded space.
    """
    
    def __init__(self):
        """
        Initializes the SupremumMetric instance.
        """
        super().__init__()
        self.resource = "metric"
        logger.debug("Initialized SupremumMetric")

    def distance(self, x: Union[Sequence, np.ndarray], y: Union[Sequence, np.ndarray]) -> float:
        """
        Computes the L∞ distance between two vectors x and y.
        
        The L∞ distance is defined as the maximum absolute difference 
        between corresponding components of the vectors.

        Args:
            x: Union[Sequence, np.ndarray]
                The first vector
            y: Union[Sequence, np.ndarray]
                The second vector

        Returns:
            float: The computed L∞ distance between x and y

        Raises:
            ValueError: If the input vectors are not of the same length
        """
        logger.debug(f"Computing distance between vectors {x} and {y}")
        
        try:
            # Convert input to numpy arrays if they are not already
            x_array = np.asarray(x)
            y_array = np.asarray(y)

            # Check if inputs are vectors (1D arrays)
            if x_array.ndim != 1 or y_array.ndim != 1:
                raise ValueError("Inputs must be 1D vectors")

            # Check if vectors have the same length
            if len(x_array) != len(y_array):
                raise ValueError("Vectors must be of the same length")

            # Compute element-wise absolute differences
            differences = np.abs(x_array - y_array)
            
            # Return the maximum difference
            return float(np.max(differences))
            
        except Exception as e:
            logger.error(f"Error computing distance: {str(e)}")
            raise ValueError("Failed to compute distance between vectors")

    def distances(self, x: Union[Sequence, np.ndarray], 
                  ys: Union[Sequence[Union[Sequence, np.ndarray]], None] = None) -> Union[float, Sequence[float]]:
        """
        Computes the L∞ distances from vector x to one or more vectors ys.

        Args:
            x: Union[Sequence, np.ndarray]
                The reference vector
            ys: Union[Sequence[Union[Sequence, np.ndarray]], None]
                Optional sequence of vectors to compute distances to

        Returns:
            Union[float, Sequence[float]]: Either a single distance or sequence of distances

        Raises:
            ValueError: If input vectors are invalid or of differing lengths
        """
        logger.debug(f"Computing distances from vector {x} to {ys}")
        
        try:
            if ys is None:
                return self.distance(x, x)
            
            return [self.distance(x, y) for y in ys]
            
        except Exception as e:
            logger.error(f"Error computing distances: {str(e)}")
            raise ValueError("Failed to compute distances")

    def check_non_negativity(self, x: Union[Sequence, np.ndarray], y: Union[Sequence, np.ndarray]) -> bool:
        """
        Checks if the non-negativity property holds: d(x, y) ≥ 0.

        Args:
            x: Union[Sequence, np.ndarray]
                The first vector
            y: Union[Sequence, np.ndarray]
                The second vector

        Returns:
            bool: True if the distance is non-negative, False otherwise
        """
        logger.debug(f"Checking non-negativity for vectors {x} and {y}")
        
        try:
            distance = self.distance(x, y)
            return distance >= 0
            
        except Exception as e:
            logger.error(f"Error checking non-negativity: {str(e)}")
            return False

    def check_identity(self, x: Union[Sequence, np.ndarray], y: Union[Sequence, np.ndarray]) -> bool:
        """
        Checks the identity of indiscernibles property: d(x, y) = 0 if and only if x = y.

        Args:
            x: Union[Sequence, np.ndarray]
                The first vector
            y: Union[Sequence, np.ndarray]
                The second vector

        Returns:
            bool: True if d(x, y) = 0 implies x = y and vice versa, False otherwise
        """
        logger.debug(f"Checking identity for vectors {x} and {y}")
        
        try:
            return self.distance(x, y) == 0
            
        except Exception as e:
            logger.error(f"Error checking identity: {str(e)}")
            return False

    def check_symmetry(self, x: Union[Sequence, np.ndarray], y: Union[Sequence, np.ndarray]) -> bool:
        """
        Checks the symmetry property: d(x, y) = d(y, x).

        Args:
            x: Union[Sequence, np.ndarray]
                The first vector
            y: Union[Sequence, np.ndarray]
                The second vector

        Returns:
            bool: True if d(x, y) = d(y, x), False otherwise
        """
        logger.debug(f"Checking symmetry for vectors {x} and {y}")
        
        try:
            d_xy = self.distance(x, y)
            d_yx = self.distance(y, x)
            return d_xy == d_yx
            
        except Exception as e:
            logger.error(f"Error checking symmetry: {str(e)}")
            return False

    def check_triangle_inequality(self, x: Union[Sequence, np.ndarray], 
                                 y: Union[Sequence, np.ndarray], 
                                 z: Union[Sequence, np.ndarray]) -> bool:
        """
        Checks the triangle inequality property: d(x, z) ≤ d(x, y) + d(y, z).

        Args:
            x: Union[Sequence, np.ndarray]
                The first vector
            y: Union[Sequence, np.ndarray]
                The intermediate vector
            z: Union[Sequence, np.ndarray]
                The third vector

        Returns:
            bool: True if d(x, z) ≤ d(x, y) + d(y, z), False otherwise
        """
        logger.debug(f"Checking triangle inequality for vectors {x}, {y}, {z}")
        
        try:
            d_xz = self.distance(x, z)
            d_xy = self.distance(x, y)
            d_yz = self.distance(y, z)
            return d_xz <= d_xy + d_yz
            
        except Exception as e:
            logger.error(f"Error checking triangle inequality: {str(e)}")
            return False