import logging
import math
from typing import List, Literal, Sequence, Union


from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.metrics.IMetric import MetricInput, MetricInputCollection
from swarmauri_core.vectors.IVector import IVector

# Configure logging
logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "EuclideanMetric")
class EuclideanMetric(MetricBase):
    """
    Euclidean metric (L2 distance) implementation.

    This class implements the standard Euclidean distance metric, which is the
    straight-line distance between two points in Euclidean space, computed as the
    square root of the sum of the squared differences between corresponding coordinates.

    The Euclidean distance satisfies all metric axioms:
    - Non-negativity: d(x,y) ≥ 0
    - Identity of indiscernibles: d(x,y) = 0 if and only if x = y
    - Symmetry: d(x,y) = d(y,x)
    - Triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)

    Attributes
    ----------
    type : Literal["EuclideanMetric"]
        The specific type of metric.
    resource : str, optional
        The resource type, defaults to METRIC.
    """

    type: Literal["EuclideanMetric"] = "EuclideanMetric"

    def distance(self, x: MetricInput, y: MetricInput) -> float:
        """
        Calculate the Euclidean distance between two points.

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point

        Returns
        -------
        float
            The Euclidean distance between x and y

        Raises
        ------
        ValueError
            If inputs have different dimensions or are incompatible
        TypeError
            If input types are not supported
        """
        logger.debug(f"Calculating Euclidean distance between {x} and {y}")

        # Handle different input types
        if isinstance(x, IVector) and isinstance(y, IVector):
            # For vector objects
            if len(x) != len(y):
                raise ValueError(
                    f"Vectors must have the same dimension: {len(x)} != {len(y)}"
                )

            # Get numeric values from vectors
            x_values = x.to_numpy()
            y_values = y.to_numpy()

            # Calculate Euclidean distance
            return math.sqrt(
                sum((x_i - y_i) ** 2 for x_i, y_i in zip(x_values, y_values))
            )

        elif (
            isinstance(x, Sequence)
            and isinstance(y, Sequence)
            and not isinstance(x, str)
            and not isinstance(y, str)
        ):
            # For general sequences (lists, tuples, etc.)
            if len(x) != len(y):
                raise ValueError(
                    f"Sequences must have the same length: {len(x)} != {len(y)}"
                )

            try:
                return math.sqrt(sum((x_i - y_i) ** 2 for x_i, y_i in zip(x, y)))
            except (TypeError, ValueError) as e:
                logger.error(f"Failed to compute Euclidean distance for sequences: {e}")
                raise ValueError(
                    f"Cannot compute Euclidean distance for sequences with non-numeric elements: {e}"
                )

        else:
            logger.error(
                f"Unsupported input types for Euclidean distance: {type(x)} and {type(y)}"
            )
            raise TypeError(
                f"Euclidean distance computation not supported for types {type(x)} and {type(y)}"
            )

    def distances(
        self,
        x: Union[MetricInput, MetricInputCollection],
        y: Union[MetricInput, MetricInputCollection],
    ) -> Union[List[float], IVector, IMatrix]:
        """
        Calculate Euclidean distances between collections of points.

        Parameters
        ----------
        x : Union[MetricInput, MetricInputCollection]
            First collection of points
        y : Union[MetricInput, MetricInputCollection]
            Second collection of points

        Returns
        -------
        Union[List[float], IVector, IMatrix]
            Matrix or vector of Euclidean distances between points in x and y

        Raises
        ------
        ValueError
            If inputs are incompatible
        TypeError
            If input types are not supported
        """
        logger.debug("Calculating Euclidean distances between collections")

        # Handle different collection types
        if isinstance(x, IMatrix) and isinstance(y, IMatrix):
            # For matrix objects - compute pairwise distances between rows
            if x.shape[1] != y.shape[1]:
                raise ValueError(
                    f"Points must have the same dimension: {x.shape[1]} != {y.shape[1]}"
                )

            # Create distance matrix
            result = [[self.distance(x_row, y_row) for y_row in y] for x_row in x]
            return result

        elif (
            isinstance(x, list)
            and isinstance(y, list)
            and all(isinstance(item, (list, tuple)) for item in x)
            and all(isinstance(item, (list, tuple)) for item in y)
        ):
            # For lists of lists/tuples (representing collections of points)

            # Check if all points have the same dimension
            x_dims = [len(point) for point in x]
            y_dims = [len(point) for point in y]

            if len(set(x_dims + y_dims)) != 1:
                raise ValueError("All points must have the same dimension")

            # Compute pairwise distances
            result = [
                [self.distance(x_point, y_point) for y_point in y] for x_point in x
            ]
            return result

        elif isinstance(x, IVector) and isinstance(y, IVector):
            # Single distance between two vectors
            return [self.distance(x, y)]

        elif isinstance(x, list) and isinstance(y, list):
            # If x and y are simple lists (not lists of lists), treat them as individual points
            if not any(isinstance(item, (list, tuple)) for item in x + y):
                return [self.distance(x, y)]
            else:
                logger.error("Inconsistent collection structure")
                raise ValueError("Inconsistent collection structure")

        else:
            logger.error(f"Unsupported collection types: {type(x)} and {type(y)}")
            raise TypeError(
                f"Euclidean distances computation not supported for types {type(x)} and {type(y)}"
            )

    def check_non_negativity(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the Euclidean metric satisfies the non-negativity axiom: d(x,y) ≥ 0.

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point

        Returns
        -------
        bool
            True if the axiom is satisfied, which is always the case for Euclidean distance
        """
        try:
            dist = self.distance(x, y)
            logger.debug(f"Checking non-negativity axiom: distance = {dist}")
            return dist >= 0  # Euclidean distance is always non-negative
        except (TypeError, ValueError) as e:
            logger.error(f"Error checking non-negativity: {e}")
            return False

    def check_identity_of_indiscernibles(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the Euclidean metric satisfies the identity of indiscernibles axiom:
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
            True if the axiom is satisfied
        """
        try:
            dist = self.distance(x, y)

            # Check if distance is zero
            is_zero_dist = (
                abs(dist) < 1e-10
            )  # Using small epsilon for floating point comparison

            # Check if points are equal
            if isinstance(x, IVector) and isinstance(y, IVector):
                is_equal = len(x) == len(y) and all(
                    abs(x_i - y_i) < 1e-10 for x_i, y_i in zip(x, y)
                )
            elif isinstance(x, Sequence) and isinstance(y, Sequence):
                is_equal = len(x) == len(y) and all(
                    abs(x_i - y_i) < 1e-10 for x_i, y_i in zip(x, y)
                )
            else:
                is_equal = x == y

            logger.debug(
                f"Checking identity axiom: distance = {dist}, points equal: {is_equal}"
            )

            # Axiom is satisfied if distance is zero iff points are equal
            return (is_zero_dist and is_equal) or (not is_zero_dist and not is_equal)

        except (TypeError, ValueError) as e:
            logger.error(f"Error checking identity of indiscernibles: {e}")
            return False

    def check_symmetry(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the Euclidean metric satisfies the symmetry axiom: d(x,y) = d(y,x).

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point

        Returns
        -------
        bool
            True if the axiom is satisfied
        """
        try:
            dist_xy = self.distance(x, y)
            dist_yx = self.distance(y, x)

            # Check if the distances are equal (within floating point precision)
            is_symmetric = abs(dist_xy - dist_yx) < 1e-10

            logger.debug(
                f"Checking symmetry axiom: d(x,y) = {dist_xy}, d(y,x) = {dist_yx}, symmetric: {is_symmetric}"
            )
            return is_symmetric

        except (TypeError, ValueError) as e:
            logger.error(f"Error checking symmetry: {e}")
            return False

    def check_triangle_inequality(
        self, x: MetricInput, y: MetricInput, z: MetricInput
    ) -> bool:
        """
        Check if the Euclidean metric satisfies the triangle inequality axiom:
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
            True if the axiom is satisfied
        """
        try:
            # Calculate the three distances
            dist_xy = self.distance(x, y)
            dist_yz = self.distance(y, z)
            dist_xz = self.distance(x, z)

            # Check triangle inequality
            satisfies_inequality = (
                dist_xz <= dist_xy + dist_yz + 1e-10
            )  # Adding epsilon for floating point precision

            logger.debug(
                f"Checking triangle inequality: d(x,z) = {dist_xz}, d(x,y) + d(y,z) = {dist_xy + dist_yz}, "
                + f"inequality satisfied: {satisfies_inequality}"
            )

            return satisfies_inequality

        except (TypeError, ValueError) as e:
            logger.error(f"Error checking triangle inequality: {e}")
            return False
