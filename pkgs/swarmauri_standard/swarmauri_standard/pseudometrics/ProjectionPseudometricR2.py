from typing import Union, List, Tuple, Any
from abc import ABC
import logging
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.pseudometrics.PseudometricBase import PseudometricBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(PseudometricBase, "ProjectionPseudometricR2")
class ProjectionPseudometricR2(PseudometricBase):
    """
    A concrete implementation of PseudometricBase that measures distance by projecting
    onto a specified coordinate axis in ℝ² space.

    This pseudometric ignores all but the specified coordinate (either x or y) when
    calculating distances. It satisfies the pseudometric properties but does not
    necessarily satisfy the identity property, as different points can have the
    same projected value.

    Attributes:
        axis: The coordinate axis to use for projection. Can be either 'x' or 'y'.
    """

    type: Literal["ProjectionPseudometricR2"] = "ProjectionPseudometricR2"

    def __init__(self, axis: str = "x"):
        """
        Initialize the ProjectionPseudometricR2 instance.

        Args:
            axis: The coordinate axis to use for projection. Must be either 'x' or 'y'.
                  Defaults to 'x'.

        Raises:
            ValueError: If the axis is not 'x' or 'y'.
        """
        super().__init__()
        if axis not in ("x", "y"):
            raise ValueError("Axis must be either 'x' or 'y'")
        self.axis = axis
        logger.debug("Initialized ProjectionPseudometricR2 with axis=%s", axis)

    def distance(
        self,
        x: Union[Tuple[float, float], List[float]],
        y: Union[Tuple[float, float], List[float]],
    ) -> float:
        """
        Calculate the distance between two points in ℝ² by projecting onto the specified axis.

        Args:
            x: The first point in ℝ² (2D vector)
            y: The second point in ℝ² (2D vector)

        Returns:
            float: The absolute difference between the specified coordinates of x and y

        Raises:
            ValueError: If either point is not a 2D vector
        """
        logger.debug("Calculating distance between %s and %s", x, y)

        if len(x) != 2 or len(y) != 2:
            raise ValueError("Both points must be 2D vectors")

        if self.axis == "x":
            return abs(x[0] - y[0])
        else:
            return abs(x[1] - y[1])

    def distances(
        self,
        x: Union[Tuple[float, float], List[float]],
        y_list: Union[
            List[Union[Tuple[float, float], List[float]]],
            Tuple[Union[Tuple[float, float], List[float]]],
        ],
    ) -> List[float]:
        """
        Calculate distances from a single point to a list of points.

        Args:
            x: The reference point in ℝ² (2D vector)
            y_list: List or tuple of points in ℝ² (2D vectors)

        Returns:
            List[float]: List of distances from x to each point in y_list

        Raises:
            ValueError: If any point is not a 2D vector
        """
        logger.debug("Calculating distances from %s to multiple points", x)

        if len(x) != 2:
            raise ValueError("Reference point must be a 2D vector")

        distances = []
        for y in y_list:
            if len(y) != 2:
                raise ValueError("All points must be 2D vectors")
            distances.append(self.distance(x, y))

        return distances

    def check_non_negativity(
        self,
        x: Union[Tuple[float, float], List[float]],
        y: Union[Tuple[float, float], List[float]],
    ) -> bool:
        """
        Check if the distance satisfies non-negativity.

        Args:
            x: The first point in ℝ² (2D vector)
            y: The second point in ℝ² (2D vector)

        Returns:
            bool: True if distance is non-negative, False otherwise
        """
        logger.debug("Checking non-negativity")
        return True  # Absolute difference is always non-negative

    def check_symmetry(
        self,
        x: Union[Tuple[float, float], List[float]],
        y: Union[Tuple[float, float], List[float]],
    ) -> bool:
        """
        Check if the distance satisfies symmetry.

        Args:
            x: The first point in ℝ² (2D vector)
            y: The second point in ℝ² (2D vector)

        Returns:
            bool: True if distance is symmetric, False otherwise
        """
        logger.debug("Checking symmetry")
        return True  # Absolute difference is symmetric

    def check_triangle_inequality(
        self,
        x: Union[Tuple[float, float], List[float]],
        y: Union[Tuple[float, float], List[float]],
        z: Union[Tuple[float, float], List[float]],
    ) -> bool:
        """
        Check if the distance satisfies triangle inequality.

        Args:
            x: The first point in ℝ² (2D vector)
            y: The second point in ℝ² (2D vector)
            z: The third point in ℝ² (2D vector)

        Returns:
            bool: True if triangle inequality holds, False otherwise
        """
        logger.debug("Checking triangle inequality")

        # Calculate distances
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)
        d_xz = self.distance(x, z)

        # Check triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)
        return d_xz <= d_xy + d_yz

    def check_weak_identity(
        self,
        x: Union[Tuple[float, float], List[float]],
        y: Union[Tuple[float, float], List[float]],
    ) -> bool:
        """
        Check if the distance satisfies weak identity of indiscernibles.

        Args:
            x: The first point in ℝ² (2D vector)
            y: The second point in ℝ² (2D vector)

        Returns:
            bool: True if distance is zero only for indistinguishable points, False otherwise
        """
        logger.debug("Checking weak identity")

        # In this pseudometric, different points can have zero distance if they share the same coordinate
        # Thus, weak identity is not satisfied
        return False
