import logging
from typing import List, Literal, Optional, Tuple, Union

import numpy as np
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.metrics.IMetric import MetricInput, MetricInputCollection
from swarmauri_core.vectors.IVector import IVector

# Logger configuration
logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "SupremumMetric")
class SupremumMetric(MetricBase):
    """
    L∞-based metric measuring largest component difference.

    This metric computes the distance between two points as the maximum absolute
    difference between their corresponding components. It is also known as the
    Chebyshev distance or the L∞ metric.

    The metric is particularly useful in bounded vector spaces where the maximum
    deviation between components is more important than the overall sum of differences.

    Attributes
    ----------
    type : Literal["SupremumMetric"]
        The type identifier for this metric implementation.
    resource : str, optional
        The resource type, defaults to METRIC.
    """

    type: Literal["SupremumMetric"] = "SupremumMetric"
    resource: Optional[str] = Field(default=ResourceTypes.METRIC.value)

    def distance(self, x: MetricInput, y: MetricInput) -> float:
        """
        Calculate the supremum (maximum) distance between two points.

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point

        Returns
        -------
        float
            The maximum absolute difference between corresponding components

        Raises
        ------
        ValueError
            If inputs have different dimensions or are incompatible
        TypeError
            If input types are not supported
        """
        logger.debug(f"Calculating supremum distance between {x} and {y}")

        try:
            # Handle different types of inputs
            if hasattr(x, "to_array") and hasattr(y, "to_array"):
                # For vector types with to_array method
                x_array = x.to_array()
                y_array = y.to_array()
                return self._calculate_supremum(x_array, y_array)

            elif isinstance(x, (list, tuple)) and isinstance(y, (list, tuple)):
                # For sequence types
                if len(x) != len(y):
                    raise ValueError(
                        f"Inputs have different dimensions: {len(x)} vs {len(y)}"
                    )
                return self._calculate_supremum(x, y)

            elif isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
                # For numpy arrays
                if x.shape != y.shape:
                    raise ValueError(
                        f"Inputs have different shapes: {x.shape} vs {y.shape}"
                    )
                return self._calculate_supremum(x, y)

            elif isinstance(x, (int, float)) and isinstance(y, (int, float)):
                # For scalar values
                return abs(x - y)

            else:
                # Try to handle other types
                try:
                    return abs(x - y)
                except TypeError:
                    raise TypeError(f"Unsupported input types: {type(x)} and {type(y)}")

        except Exception as e:
            logger.error(f"Error calculating supremum distance: {str(e)}")
            raise

    def _calculate_supremum(
        self, x: Union[List, Tuple, np.ndarray], y: Union[List, Tuple, np.ndarray]
    ) -> float:
        """
        Helper method to calculate the supremum distance between two sequences.

        Parameters
        ----------
        x : Union[List, Tuple, np.ndarray]
            First sequence
        y : Union[List, Tuple, np.ndarray]
            Second sequence

        Returns
        -------
        float
            The maximum absolute difference between corresponding elements
        """
        # Calculate absolute differences between corresponding elements
        differences = [abs(float(x_i) - float(y_i)) for x_i, y_i in zip(x, y)]

        # Return the maximum difference
        if not differences:
            return 0.0
        return max(differences)

    def distances(
        self,
        x: Union[MetricInput, MetricInputCollection],
        y: Union[MetricInput, MetricInputCollection],
    ) -> Union[List[float], IVector, IMatrix]:
        """
        Calculate distances between collections of points.

        Parameters
        ----------
        x : Union[MetricInput, MetricInputCollection]
            First collection of points
        y : Union[MetricInput, MetricInputCollection]
            Second collection of points

        Returns
        -------
        Union[List[float], IVector, IMatrix]
            Matrix or vector of distances between points in x and y

        Raises
        ------
        ValueError
            If inputs are incompatible with the metric
        TypeError
            If input types are not supported
        """
        logger.debug("Calculating supremum distances between collections")

        try:
            # Case 1: Both inputs are lists/sequences of points
            if isinstance(x, (list, tuple)) and isinstance(y, (list, tuple)):
                # Check if x is a list of lists (collection) or a single point
                x_is_collection = len(x) > 0 and isinstance(
                    x[0], (list, tuple, np.ndarray)
                )
                # Check if y is a list of lists (collection) or a single point
                y_is_collection = len(y) > 0 and isinstance(
                    y[0], (list, tuple, np.ndarray)
                )

                # Both are collections
                if x_is_collection and y_is_collection:
                    # Compute pairwise distances (distance matrix)
                    return [[self.distance(xi, yj) for yj in y] for xi in x]

                # x is a collection, y is a single point
                elif x_is_collection and not y_is_collection:
                    # Compute distances from each point in x to y
                    return [self.distance(xi, y) for xi in x]

                # x is a single point, y is a collection
                elif not x_is_collection and y_is_collection:
                    # Compute distances from x to each point in y
                    return [self.distance(x, yi) for yi in y]

                # Both are single points
                else:
                    # Compute distance between corresponding points if lists have same length
                    if len(x) != len(y):
                        raise ValueError(
                            f"Collections have different lengths: {len(x)} vs {len(y)}"
                        )
                    return [self.distance(xi, yi) for xi, yi in zip(x, y)]
            # Case 2: x is a single point, y is a collection
            elif not isinstance(x, (list, tuple)) and isinstance(y, (list, tuple)):
                return [self.distance(x, yi) for yi in y]

            # Case 3: x is a collection, y is a single point
            elif isinstance(x, (list, tuple)) and not isinstance(y, (list, tuple)):
                return [self.distance(xi, y) for xi in x]

            # Case 4: Both are matrices or vectors with special methods
            elif hasattr(x, "shape") and hasattr(y, "shape"):
                # For matrix or vector types with shape attribute
                if x.shape == y.shape:
                    # Element-wise distances
                    if hasattr(x, "to_array") and hasattr(y, "to_array"):
                        x_array = x.to_array()
                        y_array = y.to_array()
                        return self._calculate_supremum(x_array, y_array)
                else:
                    # Create a distance matrix
                    result = []
                    for i in range(x.shape[0]):
                        row = []
                        for j in range(y.shape[0]):
                            if hasattr(x, "get_row") and hasattr(y, "get_row"):
                                row.append(self.distance(x.get_row(i), y.get_row(j)))
                            else:
                                raise TypeError(
                                    "Objects have shape but no get_row method"
                                )
                        result.append(row)
                    return result

            else:
                # Case 5: Single distance calculation
                return self.distance(x, y)

        except Exception as e:
            logger.error(f"Error calculating supremum distances: {str(e)}")
            raise

    def check_non_negativity(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the metric satisfies the non-negativity axiom: d(x,y) ≥ 0.

        The supremum metric always satisfies this axiom as it's based on absolute differences.

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise
        """
        logger.debug("Checking non-negativity axiom for supremum metric")

        try:
            # Calculate the distance
            dist = self.distance(x, y)

            # Check if the distance is non-negative
            return dist >= 0
        except Exception as e:
            logger.error(f"Error checking non-negativity: {str(e)}")
            return False

    def check_identity_of_indiscernibles(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the metric satisfies the identity of indiscernibles axiom:
        d(x,y) = 0 if and only if x = y.

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise
        """
        logger.debug("Checking identity of indiscernibles axiom for supremum metric")

        try:
            # Calculate the distance
            dist = self.distance(x, y)

            # Check if the points are equal
            equal = False

            if hasattr(x, "to_array") and hasattr(y, "to_array"):
                x_array = x.to_array()
                y_array = y.to_array()
                equal = np.array_equal(x_array, y_array)
            elif isinstance(x, (list, tuple)) and isinstance(y, (list, tuple)):
                equal = x == y
            elif isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
                equal = np.array_equal(x, y)
            else:
                equal = x == y

            # Check if the axiom is satisfied
            # Distance is 0 iff the points are equal
            return (dist == 0) == equal
        except Exception as e:
            logger.error(f"Error checking identity of indiscernibles: {str(e)}")
            return False

    def check_symmetry(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the metric satisfies the symmetry axiom: d(x,y) = d(y,x).

        The supremum metric always satisfies this axiom as absolute differences are symmetric.

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise
        """
        logger.debug("Checking symmetry axiom for supremum metric")

        try:
            # Calculate distances in both directions
            dist_xy = self.distance(x, y)
            dist_yx = self.distance(y, x)

            # Check if the distances are equal (within a small epsilon for floating-point comparison)
            epsilon = 1e-10
            return abs(dist_xy - dist_yx) < epsilon
        except Exception as e:
            logger.error(f"Error checking symmetry: {str(e)}")
            return False

    def check_triangle_inequality(
        self, x: MetricInput, y: MetricInput, z: MetricInput
    ) -> bool:
        """
        Check if the metric satisfies the triangle inequality axiom:
        d(x,z) ≤ d(x,y) + d(y,z).

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point
        z : MetricInput
            Third point

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise
        """
        logger.debug("Checking triangle inequality axiom for supremum metric")

        try:
            # Calculate the three distances
            dist_xy = self.distance(x, y)
            dist_yz = self.distance(y, z)
            dist_xz = self.distance(x, z)

            # Check if the triangle inequality holds
            # Use a small epsilon for floating-point comparison
            epsilon = 1e-10
            return dist_xz <= dist_xy + dist_yz + epsilon
        except Exception as e:
            logger.error(f"Error checking triangle inequality: {str(e)}")
            return False
