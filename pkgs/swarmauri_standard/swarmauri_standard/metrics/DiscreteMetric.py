import logging
from typing import List, Literal, Union

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.metrics.IMetric import MetricInput, MetricInputCollection
from swarmauri_core.vectors.IVector import IVector

# Logger configuration
logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "DiscreteMetric")
class DiscreteMetric(MetricBase):
    """
    Discrete metric implementation.

    This metric returns 1 if two points are different and 0 if they are the same.
    It works with any hashable types and satisfies all metric axioms:
    - Non-negativity
    - Identity of indiscernibles
    - Symmetry
    - Triangle inequality

    The discrete metric is also known as the "trivial metric" or "0-1 metric".
    """

    type: Literal["DiscreteMetric"] = "DiscreteMetric"

    def distance(self, x: MetricInput, y: MetricInput) -> float:
        """
        Calculate the distance between two points: 1 if different, 0 if same.

        Parameters
        ----------
        x : MetricInput
            First point (must be hashable)
        y : MetricInput
            Second point (must be hashable)

        Returns
        -------
        float
            0.0 if x equals y, 1.0 otherwise

        Raises
        ------
        TypeError
            If inputs are not hashable
        """
        logger.debug(f"Calculating discrete distance between {x} and {y}")

        # Check if inputs are hashable
        try:
            hash(x)
            hash(y)
        except TypeError:
            error_msg = f"Inputs must be hashable, got {type(x)} and {type(y)}"
            logger.error(error_msg)
            raise TypeError(error_msg)

        # Return 0 if equal, 1 otherwise
        return 0.0 if x == y else 1.0

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
            Matrix of distances between points in x and y

        Raises
        ------
        TypeError
            If inputs are not iterable or contain non-hashable elements
        """
        logger.debug("Calculating discrete distances between collections")

        try:
            # Convert inputs to lists if they're not already
            x_list = list(x) if not isinstance(x, (int, float)) else [x]
            y_list = list(y) if not isinstance(y, (int, float)) else [y]

            # Create a distance matrix
            result = np.zeros((len(x_list), len(y_list)))

            # Fill the distance matrix
            for i, x_val in enumerate(x_list):
                for j, y_val in enumerate(y_list):
                    result[i, j] = self.distance(x_val, y_val)

            return result

        except TypeError as e:
            error_msg = f"Error calculating distances: {str(e)}"
            logger.error(error_msg)
            raise TypeError(error_msg)

    def check_non_negativity(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the metric satisfies the non-negativity axiom: d(x,y) ≥ 0.

        Always returns True for DiscreteMetric as distances are either 0 or 1.

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point

        Returns
        -------
        bool
            True (always satisfied for discrete metric)
        """
        logger.debug(f"Checking non-negativity axiom for {x} and {y}")
        # Distance is always 0 or 1, so always non-negative
        return True

    def check_identity_of_indiscernibles(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the metric satisfies the identity of indiscernibles axiom:
        d(x,y) = 0 if and only if x = y.

        Always returns True for DiscreteMetric by definition.

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point

        Returns
        -------
        bool
            True (always satisfied for discrete metric)
        """
        logger.debug(f"Checking identity of indiscernibles axiom for {x} and {y}")
        # By definition, distance is 0 if and only if x == y
        return True

    def check_symmetry(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the metric satisfies the symmetry axiom: d(x,y) = d(y,x).

        Always returns True for DiscreteMetric as equality is symmetric.

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point

        Returns
        -------
        bool
            True (always satisfied for discrete metric)
        """
        logger.debug(f"Checking symmetry axiom for {x} and {y}")
        # x == y is symmetric, so the discrete metric is symmetric
        return True

    def check_triangle_inequality(
        self, x: MetricInput, y: MetricInput, z: MetricInput
    ) -> bool:
        """
        Check if the metric satisfies the triangle inequality axiom:
        d(x,z) ≤ d(x,y) + d(y,z).

        Always returns True for DiscreteMetric.

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
            True (always satisfied for discrete metric)
        """
        logger.debug(f"Checking triangle inequality axiom for {x}, {y}, and {z}")

        # Calculate the distances
        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)

        # Check triangle inequality
        # For discrete metric, this is always satisfied:
        # If x == z, then d_xz = 0, which is ≤ d_xy + d_yz for any values
        # If x != z, then d_xz = 1, and either:
        #   - If x != y or y != z, then d_xy + d_yz ≥ 1
        #   - If x == y and y == z, then x == z (contradiction)
        return d_xz <= d_xy + d_yz
