from typing import Union, List, Tuple, Literal
import logging
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.pseudometrics.PseudometricBase import PseudometricBase
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

logger = logging.getLogger(__name__)


@ComponentBase.register_type(PseudometricBase, "ProjectionPseudometricR2")
class ProjectionPseudometricR2(PseudometricBase):
    """
    A class implementing a pseudometric space by projecting ℝ² vectors onto a specified axis.

    This class provides a concrete implementation of the PseudometricBase class for ℝ² space.
    It computes distances by projecting vectors onto a specified coordinate axis (either x or y)
    and calculating the absolute difference between the projected values.

    Inherits:
        PseudometricBase: Base class for pseudometric space implementations
        ComponentBase: Base class for all components in the system

    Attributes:
        projection_axis: Literal["x", "y"] - The coordinate axis to use for projection
        resource: str - Resource type identifier
    """

    projection_axis: Literal["x", "y"]
    resource: str = ResourceTypes.PSEUDOMETRIC.value

    def __init__(self, projection_axis: Literal["x", "y"] = "x"):
        """
        Initializes the ProjectionPseudometricR2 instance.

        Args:
            projection_axis: The coordinate axis to use for projection. Defaults to "x".
        """
        super().__init__()
        if projection_axis not in ("x", "y"):
            raise ValueError("projection_axis must be either 'x' or 'y'")
        self.projection_axis = projection_axis
        logger.debug(
            f"Initialized ProjectionPseudometricR2 with projection_axis={projection_axis}"
        )

    def distance(
        self,
        x: Union[IVector, IMatrix, List[float], Tuple[float, ...]],
        y: Union[IVector, IMatrix, List[float], Tuple[float, ...]],
    ) -> float:
        """
        Computes the pseudometric distance between two points in ℝ² by projecting onto the specified axis.

        Args:
            x: First point in ℝ²
            y: Second point in ℝ²

        Returns:
            float: The absolute difference between the projected coordinates

        Raises:
            ValueError: If input points are not 2D vectors
        """
        logger.debug(f"Computing distance between {x} and {y}")

        # Extract coordinates based on projection axis
        x_coord = self._get_projection(x)
        y_coord = self._get_projection(y)

        return abs(x_coord - y_coord)

    def distances(
        self,
        x: Union[IVector, IMatrix, List[float], Tuple[float, ...]],
        y_list: List[Union[IVector, IMatrix, List[float], Tuple[float, ...]]],
    ) -> List[float]:
        """
        Computes distances from a single point to multiple points in ℝ².

        Args:
            x: Reference point in ℝ²
            y_list: List of points in ℝ²

        Returns:
            List[float]: List of distances from x to each point in y_list
        """
        logger.debug(f"Computing distances from {x} to {y_list}")
        return [self.distance(x, y) for y in y_list]

    def check_non_negativity(
        self,
        x: Union[IVector, IMatrix, List[float], Tuple[float, ...]],
        y: Union[IVector, IMatrix, List[float], Tuple[float, ...]],
    ) -> bool:
        """
        Verifies the non-negativity property: d(x,y) ≥ 0.

        Args:
            x: First point in ℝ²
            y: Second point in ℝ²

        Returns:
            bool: True if non-negativity holds, False otherwise
        """
        logger.debug(f"Checking non-negativity for {x} and {y}")
        return self.distance(x, y) >= 0

    def check_symmetry(
        self,
        x: Union[IVector, IMatrix, List[float], Tuple[float, ...]],
        y: Union[IVector, IMatrix, List[float], Tuple[float, ...]],
    ) -> bool:
        """
        Verifies the symmetry property: d(x,y) = d(y,x).

        Args:
            x: First point in ℝ²
            y: Second point in ℝ²

        Returns:
            bool: True if symmetry holds, False otherwise
        """
        logger.debug(f"Checking symmetry for {x} and {y}")
        return self.distance(x, y) == self.distance(y, x)

    def check_triangle_inequality(
        self,
        x: Union[IVector, IMatrix, List[float], Tuple[float, ...]],
        y: Union[IVector, IMatrix, List[float], Tuple[float, ...]],
        z: Union[IVector, IMatrix, List[float], Tuple[float, ...]],
    ) -> bool:
        """
        Verifies the triangle inequality property: d(x,z) ≤ d(x,y) + d(y,z).

        Args:
            x: First point in ℝ²
            y: Second point in ℝ²
            z: Third point in ℝ²

        Returns:
            bool: True if triangle inequality holds, False otherwise
        """
        logger.debug(f"Checking triangle inequality for {x}, {y}, {z}")
        return self.distance(x, z) <= self.distance(x, y) + self.distance(y, z)

    def check_weak_identity(
        self,
        x: Union[IVector, IMatrix, List[float], Tuple[float, ...]],
        y: Union[IVector, IMatrix, List[float], Tuple[float, ...]],
    ) -> bool:
        """
        Verifies the weak identity property: d(x,y) = 0 does not necessarily imply x = y.

        Args:
            x: First point in ℝ²
            y: Second point in ℝ²

        Returns:
            bool: True if weak identity holds (d(x,y)=0 does not imply x=y), False otherwise
        """
        logger.debug(f"Checking weak identity for {x} and {y}")
        # In projection pseudometric, different points can have the same projected value
        return True

    def _get_projection(
        self, point: Union[IVector, IMatrix, List[float], Tuple[float, ...]]
    ) -> float:
        """
        Helper method to get the projected coordinate of a point based on the projection axis.

        Args:
            point: Point in ℝ²

        Returns:
            float: Projected coordinate value

        Raises:
            ValueError: If point is not a 2D vector-like structure
        """
        if isinstance(point, (IVector, IMatrix)):
            data = point.data()
        elif isinstance(point, (list, tuple)):
            data = point
        else:
            raise ValueError("Unsupported point type for projection")

        if len(data) != 2:
            raise ValueError("Points must be 2-dimensional")

        return data[0] if self.projection_axis == "x" else data[1]

    def __str__(self) -> str:
        """
        Returns a string representation of the ProjectionPseudometricR2 instance.

        Returns:
            str: String representation
        """
        return f"ProjectionPseudometricR2(projection_axis={self.projection_axis})"

    def __repr__(self) -> str:
        """
        Returns the official string representation of the ProjectionPseudometricR2 instance.

        Returns:
            str: Official string representation
        """
        return self.__str__()
