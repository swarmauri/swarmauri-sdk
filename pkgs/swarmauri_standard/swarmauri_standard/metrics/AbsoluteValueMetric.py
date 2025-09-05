import logging
from typing import List, Literal, Sequence, Union

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.metrics.IMetric import MetricInput, MetricInputCollection
from swarmauri_core.vectors.IVector import IVector

# Configure logging
logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "AbsoluteValueMetric")
class AbsoluteValueMetric(MetricBase):
    """
    Implementation of a metric based on absolute value difference.

    This is the simplest valid metric, using subtraction and the absolute value
    to calculate distance between real numbers.

    Attributes
    ----------
    type : Literal["AbsoluteValueMetric"]
        The type identifier for this metric implementation.
    resource : str, optional
        The resource type, defaults to METRIC.
    """

    type: Literal["AbsoluteValueMetric"] = "AbsoluteValueMetric"

    def distance(self, x: MetricInput, y: MetricInput) -> float:
        """
        Calculate the distance between two scalar values using absolute difference.

        Parameters
        ----------
        x : MetricInput
            First scalar value
        y : MetricInput
            Second scalar value

        Returns
        -------
        float
            The absolute difference between x and y

        Raises
        ------
        TypeError
            If inputs are not scalar numeric values
        """
        logger.debug(f"Calculating absolute value distance between {x} and {y}")

        # Validate inputs are scalar numeric values
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            logger.error(f"Invalid input types: x is {type(x)}, y is {type(y)}")
            raise TypeError("AbsoluteValueMetric requires scalar numeric inputs")

        # Calculate absolute difference
        return abs(x - y)

    def distances(
        self,
        x: Union[MetricInput, MetricInputCollection],
        y: Union[MetricInput, MetricInputCollection],
    ) -> Union[List[float], IVector, IMatrix]:
        """
        Calculate distances between collections of scalar values.

        Parameters
        ----------
        x : Union[MetricInput, MetricInputCollection]
            First collection of scalar values
        y : Union[MetricInput, MetricInputCollection]
            Second collection of scalar values

        Returns
        -------
        Union[List[float], IVector, IMatrix]
            Vector of distances if one of the inputs is a single value,
            or a matrix of pairwise distances otherwise

        Raises
        ------
        TypeError
            If inputs are not collections of scalar values
        ValueError
            If input collections have incompatible shapes
        """
        logger.debug("Calculating distances between collections")

        # Convert inputs to lists for uniform processing
        x_values = self._to_list(x)
        y_values = self._to_list(y)

        # If one input is a single value and the other is a collection
        if len(x_values) == 1 and len(y_values) > 1:
            return [self.distance(x_values[0], y_val) for y_val in y_values]
        elif len(y_values) == 1 and len(x_values) > 1:
            return [self.distance(x_val, y_values[0]) for x_val in x_values]

        # Both inputs are collections - return matrix of pairwise distances
        return [
            [self.distance(x_val, y_val) for y_val in y_values] for x_val in x_values
        ]

    def check_non_negativity(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the metric satisfies the non-negativity axiom: d(x,y) ≥ 0.

        This is always true for absolute value difference.

        Parameters
        ----------
        x : MetricInput
            First scalar value
        y : MetricInput
            Second scalar value

        Returns
        -------
        bool
            True (absolute value is always non-negative)
        """
        logger.debug(f"Checking non-negativity axiom for {x} and {y}")
        dist = self.distance(x, y)
        # Absolute value is always non-negative
        return dist >= 0

    def check_identity_of_indiscernibles(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the metric satisfies the identity of indiscernibles axiom:
        d(x,y) = 0 if and only if x = y.

        Parameters
        ----------
        x : MetricInput
            First scalar value
        y : MetricInput
            Second scalar value

        Returns
        -------
        bool
            True if the axiom is satisfied
        """
        logger.debug(f"Checking identity of indiscernibles axiom for {x} and {y}")
        dist = self.distance(x, y)

        # Check if distance is 0 iff x equals y
        return (dist == 0 and x == y) or (dist > 0 and x != y)

    def check_symmetry(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the metric satisfies the symmetry axiom: d(x,y) = d(y,x).

        Parameters
        ----------
        x : MetricInput
            First scalar value
        y : MetricInput
            Second scalar value

        Returns
        -------
        bool
            True if the axiom is satisfied
        """
        logger.debug(f"Checking symmetry axiom for {x} and {y}")

        # Calculate distances in both directions
        dist_xy = self.distance(x, y)
        dist_yx = self.distance(y, x)

        # Check if distances are equal (allowing for small floating-point errors)
        return abs(dist_xy - dist_yx) < 1e-10

    def check_triangle_inequality(
        self, x: MetricInput, y: MetricInput, z: MetricInput
    ) -> bool:
        """
        Check if the metric satisfies the triangle inequality axiom:
        d(x,z) ≤ d(x,y) + d(y,z).

        Parameters
        ----------
        x : MetricInput
            First scalar value
        y : MetricInput
            Second scalar value
        z : MetricInput
            Third scalar value

        Returns
        -------
        bool
            True if the axiom is satisfied
        """
        logger.debug(f"Checking triangle inequality axiom for {x}, {y}, and {z}")

        # Calculate all three distances
        dist_xy = self.distance(x, y)
        dist_yz = self.distance(y, z)
        dist_xz = self.distance(x, z)

        # Check triangle inequality (with small tolerance for floating-point errors)
        return dist_xz <= dist_xy + dist_yz + 1e-10

    def _to_list(self, x: MetricInput) -> List[float]:
        """
        Convert various input types to a list of floats.

        Parameters
        ----------
        x : MetricInput
            Input to convert

        Returns
        -------
        List[float]
            List representation of the input

        Raises
        ------
        TypeError
            If input cannot be converted to a list of floats
        """
        # Handle single scalar value
        if isinstance(x, (int, float)):
            return [float(x)]

        # Handle list
        elif isinstance(x, list):
            if all(isinstance(val, (int, float)) for val in x):
                return [float(val) for val in x]
            else:
                raise TypeError("All elements in list must be numeric")

        # Handle numpy array
        elif isinstance(x, np.ndarray):
            if x.ndim == 1:
                return x.astype(float).tolist()
            else:
                raise ValueError("Only 1D arrays are supported")

        # Handle IVector
        elif isinstance(x, IVector):
            return [float(val) for val in x.value]

        # Handle other sequence types
        elif isinstance(x, Sequence) and not isinstance(x, str):
            try:
                return [float(val) for val in x]
            except (ValueError, TypeError):
                raise TypeError("Cannot convert sequence elements to float")

        # Handle dictionary
        elif isinstance(x, dict):
            try:
                return [float(val) for val in x.values()]
            except (ValueError, TypeError):
                raise TypeError("Cannot convert dictionary values to float")

        else:
            raise TypeError(f"Cannot convert type {type(x)} to list of floats")
