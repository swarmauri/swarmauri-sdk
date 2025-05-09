import logging
from typing import TypeVar, Union, Sequence, Optional, Tuple, Any
import numpy as np
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase

T = TypeVar("T", Union["IVector", "IMatrix", Sequence, Tuple, np.ndarray, Any])


@ComponentBase.register_type(MetricBase, "SupremumMetric")
class SupremumMetric(MetricBase):
    """
    Provides a concrete implementation of the L∞ metric, which measures the maximum
    deviation between corresponding components of two vectors.

    Inherits From:
        MetricBase: Base class providing common interfaces for metric computations.
        ComponentBase: Base class for all components in the system.

    Implements:
        - distance(): Computes the L∞ distance between two points
        - distances(): Computes distances between a point and multiple points
        - Various metric axiom verification methods

    Attributes:
        type: Literal["SupremumMetric"] = "SupremumMetric"
            Type identifier for the metric class
    """

    type: Literal["SupremumMetric"] = "SupremumMetric"
    resource: Optional[str] = Field(default="Metric")

    def __init__(self):
        """
        Initializes the SupremumMetric instance.

        Sets up logging and initializes the base class.
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.debug("SupremumMetric instance initialized")

    def distance(self, x: T, y: T) -> float:
        """
        Computes the L∞ distance between two points.

        The L∞ distance is defined as the maximum absolute difference between
        corresponding components of the two points.

        Args:
            x: T
                The first point to compare
            y: T
                The second point to compare

        Returns:
            float:
                The computed L∞ distance between x and y

        Raises:
            ValueError:
                If the input shapes are incompatible
            TypeError:
                If the input types are not supported
        """
        self.logger.debug("Computing L∞ distance between points")

        try:
            # Convert inputs to numpy arrays if they're not already
            x_arr = np.asarray(x)
            y_arr = np.asarray(y)

            # Ensure same shape
            if x_arr.shape != y_arr.shape:
                raise ValueError("Input shapes must match for distance computation")

            # Compute element-wise absolute differences
            differences = np.abs(x_arr - y_arr)

            # Return the maximum difference
            return float(np.amax(differences))

        except Exception as e:
            self.logger.error(f"Error computing distance: {str(e)}")
            raise e

    def distances(
        self, x: T, y_list: Union[T, Sequence[T]]
    ) -> Union[float, Sequence[float]]:
        """
        Computes the L∞ distances from a reference point to one or more points.

        Args:
            x: T
                The reference point
            y_list: Union[T, Sequence[T]]
                Either a single point or a sequence of points

        Returns:
            Union[float, Sequence[float]]:
                - If y_list is a single point: Returns the distance as a float
                - If y_list is a sequence: Returns a sequence of distances

        Raises:
            ValueError:
                If input types are incompatible
            TypeError:
                If input types are not supported
        """
        self.logger.debug("Computing L∞ distances to reference point")

        if isinstance(y_list, Sequence):
            try:
                return [self.distance(x, y) for y in y_list]
            except Exception as e:
                self.logger.error(f"Error computing distances: {str(e)}")
                raise e
        else:
            return self.distance(x, y_list)

    def check_non_negativity(self, x: T, y: T) -> bool:
        """
        Verifies the non-negativity axiom for the L∞ metric.

        Args:
            x: T
                The first point
            y: T
                The second point

        Returns:
            bool:
                True if the non-negativity condition holds, False otherwise
        """
        self.logger.debug("Checking non-negativity axiom")
        distance = self.distance(x, y)
        return distance >= 0.0

    def check_identity(self, x: T, y: T) -> bool:
        """
        Verifies the identity of indiscernibles axiom for the L∞ metric.

        Args:
            x: T
                The first point
            y: T
                The second point

        Returns:
            bool:
                True if x and y are identical according to the metric, False otherwise
        """
        self.logger.debug("Checking identity of indiscernibles axiom")
        return self.distance(x, y) == 0.0

    def check_symmetry(self, x: T, y: T) -> bool:
        """
        Verifies the symmetry axiom for the L∞ metric.

        Args:
            x: T
                The first point
            y: T
                The second point

        Returns:
            bool:
                True if the symmetry condition holds, False otherwise
        """
        self.logger.debug("Checking symmetry axiom")
        return self.distance(x, y) == self.distance(y, x)

    def check_triangle_inequality(self, x: T, y: T, z: T) -> bool:
        """
        Verifies the triangle inequality axiom for the L∞ metric.

        Args:
            x: T
                The first point
            y: T
                The second point
            z: T
                The third point

        Returns:
            bool:
                True if the triangle inequality condition holds, False otherwise
        """
        self.logger.debug("Checking triangle inequality axiom")
        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)
        return d_xz <= d_xy + d_yz
