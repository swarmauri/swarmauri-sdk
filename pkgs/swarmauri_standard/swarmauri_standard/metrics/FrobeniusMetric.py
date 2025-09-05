import logging
from typing import List, Literal, Optional, Sequence, Union

import numpy as np
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.metrics.IMetric import MetricInput, MetricInputCollection
from swarmauri_core.vectors.IVector import IVector

# Configure logging
logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "FrobeniusMetric")
class FrobeniusMetric(MetricBase):
    """
    Implementation of the Frobenius metric for matrices.

    The Frobenius metric calculates the distance between two matrices as the
    square root of the sum of squared differences of their entries.

    Attributes
    ----------
    type : Literal["FrobeniusMetric"]
        The specific type of metric.
    resource : str, optional
        The resource type, defaults to METRIC.
    """

    type: Literal["FrobeniusMetric"] = "FrobeniusMetric"
    resource: Optional[str] = Field(default=ResourceTypes.METRIC.value)

    def distance(self, x: MetricInput, y: MetricInput) -> float:
        """
        Calculate the Frobenius distance between two matrices.

        Parameters
        ----------
        x : MetricInput
            First matrix
        y : MetricInput
            Second matrix

        Returns
        -------
        float
            The Frobenius distance between x and y

        Raises
        ------
        ValueError
            If matrices have different shapes
        TypeError
            If inputs are not matrices
        """
        logger.debug(
            f"Calculating Frobenius distance between matrices of types {type(x)} and {type(y)}"
        )

        # Convert inputs to numpy arrays for easier processing
        if isinstance(x, IMatrix):
            x_array = np.array(x)
        elif isinstance(x, (np.ndarray, list)):
            x_array = np.array(x)
        else:
            raise TypeError(f"Unsupported type for Frobenius metric: {type(x)}")

        if isinstance(y, IMatrix):
            y_array = np.array(y)
        elif isinstance(y, (np.ndarray, list)):
            y_array = np.array(y)
        else:
            raise TypeError(f"Unsupported type for Frobenius metric: {type(y)}")

        # Check if matrices have the same shape
        if x_array.shape != y_array.shape:
            error_msg = f"Matrices must have the same shape. Got {x_array.shape} and {y_array.shape}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Calculate the Frobenius distance
        # sqrt(sum((x_ij - y_ij)^2))
        diff = x_array - y_array
        frobenius_distance = np.sqrt(np.sum(diff * diff))

        logger.debug(f"Frobenius distance calculated: {frobenius_distance}")
        return float(frobenius_distance)

    def distances(
        self,
        x: Union[MetricInput, MetricInputCollection],
        y: Union[MetricInput, MetricInputCollection],
    ) -> Union[List[float], IVector, IMatrix]:
        """
        Calculate Frobenius distances between collections of matrices.

        Parameters
        ----------
        x : Union[MetricInput, MetricInputCollection]
            First collection of matrices
        y : Union[MetricInput, MetricInputCollection]
            Second collection of matrices

        Returns
        -------
        Union[List[float], IVector, IMatrix]
            Matrix of distances between matrices in x and y

        Raises
        ------
        ValueError
            If inputs are incompatible
        TypeError
            If input types are not supported
        """
        logger.debug("Calculating Frobenius distances between collections of matrices")

        if not isinstance(x, (list, tuple, Sequence)) or not isinstance(
            y, (list, tuple, Sequence)
        ):
            raise TypeError("Both inputs must be collections of matrices")

        # Calculate pairwise distances
        distance_matrix = []
        for x_i in x:
            row = []
            for y_j in y:
                try:
                    dist = self.distance(x_i, y_j)
                    row.append(dist)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error calculating distance: {e}")
                    row.append(float("nan"))
            distance_matrix.append(row)

        return distance_matrix

    def check_non_negativity(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the Frobenius metric satisfies the non-negativity axiom: d(x,y) ≥ 0.

        The Frobenius metric always satisfies this axiom by definition.

        Parameters
        ----------
        x : MetricInput
            First matrix
        y : MetricInput
            Second matrix

        Returns
        -------
        bool
            True if the axiom is satisfied (always true for Frobenius metric)
        """
        logger.debug("Checking non-negativity axiom for Frobenius metric")
        try:
            distance_value = self.distance(x, y)
            return distance_value >= 0
        except (ValueError, TypeError) as e:
            logger.error(f"Error checking non-negativity: {e}")
            return False

    def check_identity_of_indiscernibles(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the Frobenius metric satisfies the identity of indiscernibles axiom:
        d(x,y) = 0 if and only if x = y.

        Parameters
        ----------
        x : MetricInput
            First matrix
        y : MetricInput
            Second matrix

        Returns
        -------
        bool
            True if the axiom is satisfied
        """
        logger.debug("Checking identity of indiscernibles axiom for Frobenius metric")
        try:
            distance_value = self.distance(x, y)

            # Convert inputs to numpy arrays for comparison
            if isinstance(x, IMatrix):
                x_array = np.array(x)
            else:
                x_array = np.array(x)

            if isinstance(y, IMatrix):
                y_array = np.array(y)
            else:
                y_array = np.array(y)

            # Check if matrices are equal
            matrices_equal = np.array_equal(x_array, y_array)

            # Check the axiom: d(x,y) = 0 iff x = y
            if (
                abs(distance_value) < 1e-10
            ):  # Using small epsilon for floating-point comparison
                return matrices_equal
            else:
                return not matrices_equal

        except (ValueError, TypeError) as e:
            logger.error(f"Error checking identity of indiscernibles: {e}")
            return False

    def check_symmetry(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the Frobenius metric satisfies the symmetry axiom: d(x,y) = d(y,x).

        Parameters
        ----------
        x : MetricInput
            First matrix
        y : MetricInput
            Second matrix

        Returns
        -------
        bool
            True if the axiom is satisfied
        """
        logger.debug("Checking symmetry axiom for Frobenius metric")
        try:
            distance_xy = self.distance(x, y)
            distance_yx = self.distance(y, x)

            # Check if distances are equal (within floating-point precision)
            return abs(distance_xy - distance_yx) < 1e-10

        except (ValueError, TypeError) as e:
            logger.error(f"Error checking symmetry: {e}")
            return False

    def check_triangle_inequality(
        self, x: MetricInput, y: MetricInput, z: MetricInput
    ) -> bool:
        """
        Check if the Frobenius metric satisfies the triangle inequality axiom:
        d(x,z) ≤ d(x,y) + d(y,z).

        Parameters
        ----------
        x : MetricInput
            First matrix
        y : MetricInput
            Second matrix
        z : MetricInput
            Third matrix

        Returns
        -------
        bool
            True if the axiom is satisfied
        """
        logger.debug("Checking triangle inequality axiom for Frobenius metric")
        try:
            distance_xz = self.distance(x, z)
            distance_xy = self.distance(x, y)
            distance_yz = self.distance(y, z)

            # Check triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)
            # Add small epsilon for floating-point comparison
            return distance_xz <= distance_xy + distance_yz + 1e-10

        except (ValueError, TypeError) as e:
            logger.error(f"Error checking triangle inequality: {e}")
            return False
