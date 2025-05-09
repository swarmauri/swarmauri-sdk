import logging
from typing import Union, Any, Sequence, Optional
import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics import MetricBase
from swarmauri_core.vectors import IVector
from swarmauri_core.matrices import IMatrix

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "FrobeniusMetric")
class FrobeniusMetric(MetricBase):
    """
    Concrete implementation of the MetricBase class for computing the Frobenius metric between matrices.
    
    The Frobenius metric is defined as the square root of the sum of the squares of the differences between
    corresponding matrix elements. This class handles various input types including matrices, vectors, 
    sequences, strings, and callables.
    """
    
    type: Literal["FrobeniusMetric"] = "FrobeniusMetric"

    def __init__(self):
        """
        Initializes the FrobeniusMetric instance.
        """
        super().__init__()

    def distance(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                  y: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Computes the Frobenius distance metric between two matrices x and y.
        
        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first matrix/vector to compute distance from
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second matrix/vector to compute distance to
                
        Returns:
            float: The computed Frobenius distance between x and y

        Raises:
            ValueError: If the input shapes are not compatible
        """
        logger.debug(f"Computing Frobenius distance between inputs: {x} and {y}")
        
        try:
            # Convert inputs to numpy arrays
            x_np = self._convert_to_numpy(x)
            y_np = self._convert_to_numpy(y)
            
            # Validate shapes
            if not np.shape_equal(x_np.shape, y_np.shape):
                raise ValueError(f"Input shapes must match. Got {x_np.shape} and {y_np.shape}")
            
            # Compute element-wise differences and Frobenius norm
            difference = x_np - y_np
            squared_diff = difference ** 2
            sum_squared = np.sum(squared_diff)
            
            logger.debug(f"Frobenius distance computed as: {sum_squared}")
            return float(sum_squared)
            
        except Exception as e:
            logger.error(f"Error computing Frobenius distance: {str(e)}")
            raise

    def distances(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                  ys: Union[Sequence[Union[IVector, IMatrix, Sequence, str, Callable]], None] = None) -> Union[float, Sequence[float]]:
        """
        Computes the Frobenius distance(s) from point x to one or more points y(s).
        
        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The reference point
            ys: Union[Sequence[Union[IVector, IMatrix, Sequence, str, Callable]], None]
                Optional sequence of points to compute distances to
                
        Returns:
            Union[float, Sequence[float]]: Either a single distance or sequence of distances
        """
        logger.debug(f"Computing Frobenius distances from input: {x} to inputs: {ys}")
        
        if ys is None:
            return self.distance(x, ys)
            
        try:
            return [self.distance(x, y) for y in ys]
            
        except Exception as e:
            logger.error(f"Error computing Frobenius distances: {str(e)}")
            raise

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
        distance = self.distance(x, y)
        return distance >= 0

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
        distance = self.distance(x, y)
        return distance == 0

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
        d_xy = self.distance(x, y)
        d_yx = self.distance(y, x)
        return d_xy == d_yx

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
        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)
        return d_xz <= d_xy + d_yz

    def _convert_to_numpy(self, input: Union[IVector, IMatrix, Sequence, str, Callable]) -> np.ndarray:
        """
        Converts various input types to a numpy array for computation.
        
        Args:
            input: Union[IVector, IMatrix, Sequence, str, Callable]
                The input to convert
                
        Returns:
            np.ndarray: The converted numpy array
                
        Raises:
            ValueError: If the input type is not supported
        """
        try:
            if isinstance(input, (IVector, IMatrix)):
                return input.to_numpy()
            elif isinstance(input, Sequence):
                return np.array(input)
            elif isinstance(input, str):
                # Treat string as a sequence of characters' ASCII values
                return np.array([ord(c) for c in input])
            elif callable(input):
                # Assume the callable returns a vector-like object
                result = input()
                if isinstance(result, (IVector, IMatrix, Sequence)):
                    return np.array(result.to_list() if isinstance(result, (IVector, IMatrix)) else result)
                else:
                    raise ValueError("Callable did not return a supported type.")
            else:
                raise ValueError(f"Unsupported input type: {type(input).__name__}")
                
        except Exception as e:
            logger.error(f"Error converting input to numpy array: {str(e)}")
            raise

    def __str__(self) -> str:
        """
        Returns a string representation of the FrobeniusMetric instance.
        
        Returns:
            str: The string representation
        """
        return "FrobeniusMetric()"

    def __repr__(self) -> str:
        """
        Returns the string representation for the FrobeniusMetric class.
        
        Returns:
            str: The string representation
        """
        return "FrobeniusMetric()"