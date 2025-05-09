from typing import Union, Sequence, Optional, Literal
from abc import ABC
import logging
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.metrics.IMetric import IMetric
from swarmauri_standard.swarmauri_standard.norms import SobolevNorm

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "SobolevMetric")
class SobolevMetric(MetricBase):
    """
    A class implementing the Sobolev metric, which combines function value differences and 
    derivative differences for smoothness measurement.

    Inherits from MetricBase and implements the IMetric interface. This metric is 
    particularly useful for evaluating distances between functions with consideration 
    of their smoothness properties.
    """
    type: Literal["SobolevMetric"] = "SobolevMetric"
    
    def __init__(self, order: int = 2, alpha: float = 1.0):
        """
        Initialize the SobolevMetric instance.

        Args:
            order: The maximum derivative order to consider in the metric. Default is 2.
            alpha: Weighting factor for the derivative terms. Default is 1.0.
        """
        super().__init__()
        self.order = order
        self.alpha = alpha
        self.sobolev_norm = SobolevNorm(order=order, alpha=alpha)
        logger.debug("Initialized SobolevMetric with order %d and alpha %.2f", order, alpha)

    def distance(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                  y: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Computes the Sobolev distance metric between two functions x and y.

        The distance is computed as the Sobolev norm of the difference between the two functions.
        This incorporates both the function values and their derivatives up to the specified order.

        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first function to compute distance from
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second function to compute distance to

        Returns:
            float: The computed Sobolev distance between x and y

        Raises:
            ValueError: If either x or y is not a callable function
        """
        logger.debug("Computing Sobolev distance between functions %s and %s", x, y)
        
        if not callable(x) or not callable(y):
            raise ValueError("Both inputs must be callable functions for Sobolev metric computation")

        # Define the difference function
        def difference_function(t):
            return x(t) - y(t)

        # Compute the Sobolev norm of the difference function
        distance = self.sobolev_norm.compute(difference_function)
        logger.debug("Computed Sobolev distance: %.4f", distance)
        return distance

    def distances(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                  ys: Union[Sequence[Union[IVector, IMatrix, Sequence, str, Callable]], None] = None) -> Union[float, Sequence[float]]:
        """
        Computes the distance metric(s) from function x to one or more functions ys.

        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The reference function
            ys: Union[Sequence[Union[IVector, IMatrix, Sequence, str, Callable]], None]
                Optional sequence of functions to compute distances to

        Returns:
            Union[float, Sequence[float]]: Either a single distance or sequence of distances
        """
        logger.debug("Computing Sobolev distances from function %s to %s", x, ys)
        
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
                The first function
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second function

        Returns:
            bool: True if d(x, y) ≥ 0, False otherwise
        """
        logger.debug("Checking non-negativity")
        distance = self.distance(x, y)
        return distance >= 0

    def check_identity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                      y: Union[IVector, IMatrix, Sequence, str, Callable]) -> bool:
        """
        Checks the identity of indiscernibles property: d(x, y) = 0 if and only if x = y.

        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first function
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second function

        Returns:
            bool: True if d(x, y) = 0 implies x = y and vice versa, False otherwise
        """
        logger.debug("Checking identity")
        return self.distance(x, y) == 0

    def check_symmetry(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                     y: Union[IVector, IMatrix, Sequence, str, Callable]) -> bool:
        """
        Checks the symmetry property: d(x, y) = d(y, x).

        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first function
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second function

        Returns:
            bool: True if d(x, y) = d(y, x), False otherwise
        """
        logger.debug("Checking symmetry")
        return self.distance(x, y) == self.distance(y, x)

    def check_triangle_inequality(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                                  y: Union[IVector, IMatrix, Sequence, str, Callable], 
                                  z: Union[IVector, IMatrix, Sequence, str, Callable]) -> bool:
        """
        Checks the triangle inequality property: d(x, z) ≤ d(x, y) + d(y, z).

        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first function
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The intermediate function
            z: Union[IVector, IMatrix, Sequence, str, Callable]
                The third function

        Returns:
            bool: True if d(x, z) ≤ d(x, y) + d(y, z), False otherwise
        """
        logger.debug("Checking triangle inequality")
        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)
        return d_xz <= d_xy + d_yz

    def __str__(self) -> str:
        """
        Return a string representation of the metric object.
        """
        return f"SobolevMetric(order={self.order}, alpha={self.alpha})"

    def __repr__(self) -> str:
        """
        Return a string representation of the metric object that could be used to recreate it.
        """
        return f"SobolevMetric(order={self.order}, alpha={self.alpha})"