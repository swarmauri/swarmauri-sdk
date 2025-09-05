import logging
from typing import List, Literal, Optional, Sequence, Union

import numpy as np
from pydantic import Field, field_validator
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.metrics.IMetric import MetricInput, MetricInputCollection
from swarmauri_core.vectors.IVector import IVector

from swarmauri_standard.norms.GeneralLpNorm import GeneralLpNorm

# Logger configuration
logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "LpMetric")
class LpMetric(MetricBase):
    """
    Lp metric implementation for measuring distances between points.

    This class implements the Lp metric (Minkowski distance) which is a generalization
    of the Euclidean, Manhattan, and Chebyshev distances. The Lp distance between
    two points x and y is defined as (sum(|x_i - y_i|^p))^(1/p) for p > 1.

    Attributes
    ----------
    type : Literal["LpMetric"]
        The type identifier for this metric.
    p : floats
        The parameter p for the Lp metric. Must be finite and greater than 1.
    resource : str, optional
        The resource type, defaults to METRIC.
    """

    type: Literal["LpMetric"] = "LpMetric"
    p: float = Field(..., description="Parameter p for the Lp metric (must be > 1)")
    resource: Optional[str] = Field(default=ResourceTypes.METRIC.value)

    @field_validator("p")
    def validate_p(cls, v):
        """
        Validate that p is greater than 1 and finite.

        Parameters
        ----------
        v : float
            The value to validate.

        Returns
        -------
        float
            The validated value.

        Raises
        ------
        ValueError
            If p is not greater than 1 or is not finite.
        """
        if v <= 1:
            raise ValueError(f"Parameter p must be greater than 1, got {v}")
        if not np.isfinite(v):
            raise ValueError(f"Parameter p must be finite, got {v}")
        return v

    def _convert_to_array(self, x: MetricInput) -> np.ndarray:
        """
        Convert the input to a numpy array for computation.

        Parameters
        ----------
        x : MetricInput
            The input to convert.

        Returns
        -------
        np.ndarray
            The converted numpy array.

        Raises
        ------
        TypeError
            If the input type is not supported.
        """
        if isinstance(x, IVector):
            return x.to_numpy()
        elif isinstance(x, IMatrix):
            return x.to_array().flatten()
        elif isinstance(x, Sequence) and not isinstance(x, str):
            return np.array(x, dtype=float)
        elif isinstance(x, str):
            return np.array([ord(c) for c in x], dtype=float)
        elif isinstance(x, (int, float)):
            return np.array([x], dtype=float)
        else:
            raise TypeError(f"Unsupported input type: {type(x)}")

    def distance(self, x: MetricInput, y: MetricInput) -> float:
        """
        Calculate the Lp distance between two points.

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point

        Returns
        -------
        float
            The Lp distance between x and y

        Raises
        ------
        ValueError
            If inputs are incompatible with the metric
        TypeError
            If input types are not supported
        """
        try:
            # Convert inputs to numpy arrays
            x_array = self._convert_to_array(x)
            y_array = self._convert_to_array(y)

            # Ensure arrays have the same shape
            if x_array.shape != y_array.shape:
                raise ValueError(
                    f"Inputs must have the same shape. Got {x_array.shape} and {y_array.shape}"
                )

            # Calculate Lp distance: (sum(|x_i - y_i|^p))^(1/p)
            distance_value = np.sum(np.abs(x_array - y_array) ** self.p) ** (1 / self.p)

            logger.debug(f"Calculated Lp distance with p={self.p}: {distance_value}")
            return float(distance_value)
        except Exception as e:
            logger.error(f"Error calculating Lp distance: {str(e)}")
            raise

    def distances(
        self,
        x: Union[MetricInput, MetricInputCollection],
        y: Union[MetricInput, MetricInputCollection],
    ) -> Union[List[float], IVector, IMatrix]:
        """
        Calculate Lp distances between collections of points.

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
        try:
            # Handle different types of collections
            if isinstance(x, List) and isinstance(y, List):
                # Calculate pairwise distances between lists of points
                result = []
                for xi in x:
                    row = []
                    for yi in y:
                        row.append(self.distance(xi, yi))
                    result.append(row)

                # If one of the inputs is a single point, return a flat list
                if len(x) == 1:
                    return result[0]
                elif len(y) == 1:
                    return [row[0] for row in result]
                else:
                    return result

            elif isinstance(x, IVector) and isinstance(y, IVector):
                # Calculate distance between two vectors
                return self.distance(x, y)

            elif isinstance(x, IMatrix) and isinstance(y, IMatrix):
                # Calculate element-wise distances between matrices
                x_array = x.to_array()
                y_array = y.to_array()

                if x_array.shape != y_array.shape:
                    raise ValueError(
                        f"Matrices must have the same shape. Got {x_array.shape} and {y_array.shape}"
                    )

                # Calculate element-wise distances
                distances_array = np.sum(
                    np.abs(x_array - y_array) ** self.p, axis=-1
                ) ** (1 / self.p)

                # Convert back to appropriate type (assuming matrix implementation has from_array method)
                # This is a simplification - actual implementation depends on the IMatrix implementation
                return distances_array.tolist()

            else:
                # Handle generic case - try to compute distance directly
                return self.distance(x, y)

        except Exception as e:
            logger.error(f"Error calculating Lp distances: {str(e)}")
            raise

    def check_non_negativity(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the Lp metric satisfies the non-negativity axiom: d(x,y) ≥ 0.

        The Lp metric is always non-negative by definition.

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
        try:
            distance_value = self.distance(x, y)
            result = distance_value >= 0
            logger.debug(f"Non-negativity check result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in non-negativity check: {str(e)}")
            return False

    def check_identity_of_indiscernibles(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the Lp metric satisfies the identity of indiscernibles axiom:
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
        try:
            distance_value = self.distance(x, y)

            # Convert inputs to numpy arrays for comparison
            x_array = self._convert_to_array(x)
            y_array = self._convert_to_array(y)

            # Check if x and y are equal (all elements are equal)
            are_equal = np.array_equal(x_array, y_array)
            distance_is_zero = np.isclose(distance_value, 0)

            # The axiom is satisfied if:
            # 1. x = y and d(x,y) = 0, or
            # 2. x ≠ y and d(x,y) > 0
            result = (are_equal and distance_is_zero) or (
                not are_equal and not distance_is_zero
            )

            logger.debug(f"Identity of indiscernibles check result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in identity of indiscernibles check: {str(e)}")
            return False

    def check_symmetry(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the Lp metric satisfies the symmetry axiom: d(x,y) = d(y,x).

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
        try:
            distance_xy = self.distance(x, y)
            distance_yx = self.distance(y, x)

            # Check if distances are equal
            result = np.isclose(distance_xy, distance_yx)

            logger.debug(f"Symmetry check result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in symmetry check: {str(e)}")
            return False

    def check_triangle_inequality(
        self, x: MetricInput, y: MetricInput, z: MetricInput
    ) -> bool:
        """
        Check if the Lp metric satisfies the triangle inequality axiom:
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
        try:
            distance_xy = self.distance(x, y)
            distance_yz = self.distance(y, z)
            distance_xz = self.distance(x, z)

            # Check if triangle inequality holds
            # Adding small epsilon for numerical stability
            result = distance_xz <= distance_xy + distance_yz + 1e-10

            logger.debug(f"Triangle inequality check result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in triangle inequality check: {str(e)}")
            return False

    def get_norm(self) -> GeneralLpNorm:
        """
        Get the corresponding Lp norm for this metric.

        Returns
        -------
        GeneralLpNorm
            The Lp norm with the same p parameter
        """
        return GeneralLpNorm(p=self.p)
