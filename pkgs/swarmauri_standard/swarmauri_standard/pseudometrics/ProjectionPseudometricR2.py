from typing import Iterable, TypeVar, Optional, Union
from pydantic import Field
import logging
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.pseudometrics.IPseudometric import IPseudometric

# Configure logging
logger = logging.getLogger(__name__)

# Define type variables for input types
InputTypes = TypeVar("InputTypes", list, tuple, Iterable)
DistanceInput = TypeVar("DistanceInput", InputTypes, Iterable[InputTypes])


@ComponentBase.register_type(PseudometricBase, "ProjectionPseudometricR2")
class ProjectionPseudometricR2(PseudometricBase):
    """
    A concrete implementation of the PseudometricBase class that measures pseudometric
    via projection in ℝ². This class projects 2D vectors onto a specified coordinate
    axis (either x or y) and computes distances based on these projections.

    Attributes:
        axis: str
            The coordinate axis to use for projection. Can be either 'x' or 'y'.
            Defaults to 'x'.
        resource: str
            The resource type identifier for this component.
    """

    resource: str = Field(default=ResourceTypes.PSEUDOMETRIC.value)
    axis: str = Field(default="x")

    def __init__(self, axis: str = "x"):
        """
        Initialize the ProjectionPseudometricR2 instance.

        Args:
            axis: str
                The coordinate axis to use for projection. Must be either 'x' or 'y'.
                Defaults to 'x'.

        Raises:
            ValueError:
                If the specified axis is neither 'x' nor 'y'.
        """
        super().__init__()
        if axis not in ("x", "y"):
            raise ValueError("Axis must be either 'x' or 'y'")
        self.axis = axis
        logger.debug(f"Initialized ProjectionPseudometricR2 with axis={self.axis}")

    def distance(self, x: InputTypes, y: InputTypes) -> float:
        """
        Compute the distance between two points x and y based on their projection.

        Args:
            x: InputTypes
                The first point. Must be a 2D vector or point.
            y: InputTypes
                The second point. Must be a 2D vector or point.

        Returns:
            float:
                The distance between the projections of x and y.

        Raises:
            ValueError:
                If the input points are not 2D or not iterable.
        """
        try:
            # Extract the appropriate coordinate based on the axis
            x_coord = x[0] if self.axis == "x" else x[1]
            y_coord = y[0] if self.axis == "x" else y[1]

            # Compute the absolute difference
            return abs(x_coord - y_coord)

        except (TypeError, IndexError) as e:
            logger.error("Invalid input types for distance calculation: %s", str(e))
            raise ValueError("Inputs must be 2D points or vectors")

    def distances(self, x: InputTypes, ys: Iterable[InputTypes]) -> Iterable[float]:
        """
        Compute distances from point x to multiple points ys.

        Args:
            x: InputTypes
                The reference point. Must be a 2D vector or point.
            ys: Iterable[InputTypes]
                An iterable of points to compute distances to.

        Returns:
            Iterable[float]:
                An iterable of distances from x to each point in ys.
        """
        try:
            # Extract the appropriate coordinate for x
            x_coord = x[0] if self.axis == "x" else x[1]

            # Compute distances for each point in ys
            return (abs(x_coord - (y[0] if self.axis == "x" else y[1])) for y in ys)

        except (TypeError, IndexError) as e:
            logger.error("Invalid input types for distances calculation: %s", str(e))
            raise ValueError("Inputs must be 2D points or vectors")

    def check_non_negativity(self, x: InputTypes, y: InputTypes) -> bool:
        """
        Check if the distance satisfies non-negativity.

        Args:
            x: InputTypes
                The first point.
            y: InputTypes
                The second point.

        Returns:
            bool:
                True if distance(x, y) >= 0, False otherwise.
        """
        return True  # Absolute value is always non-negative

    def check_symmetry(self, x: InputTypes, y: InputTypes) -> bool:
        """
        Check if the distance satisfies symmetry.

        Args:
            x: InputTypes
                The first point.
            y: InputTypes
                The second point.

        Returns:
            bool:
                True if distance(x, y) == distance(y, x), False otherwise.
        """
        return True  # Absolute value difference is symmetric

    def check_triangle_inequality(
        self, x: InputTypes, y: InputTypes, z: InputTypes
    ) -> bool:
        """
        Check if the distance satisfies the triangle inequality.

        Args:
            x: InputTypes
                The first point.
            y: InputTypes
                The second point.
            z: InputTypes
                The third point.

        Returns:
            bool:
                True if distance(x, z) <= distance(x, y) + distance(y, z), False otherwise.
        """
        try:
            d_xz = self.distance(x, z)
            d_xy = self.distance(x, y)
            d_yz = self.distance(y, z)
            return d_xz <= d_xy + d_yz

        except Exception as e:
            logger.error("Error during triangle inequality check: %s", str(e))
            return False

    def check_weak_identity(self, x: InputTypes, y: InputTypes) -> bool:
        """
        Check if the distance satisfies weak identity of indiscernibles.

        Args:
            x: InputTypes
                The first point.
            y: InputTypes
                The second point.

        Returns:
            bool:
                True if x == y implies distance(x, y) == 0, False otherwise.
        """
        try:
            # Extract coordinates
            x_coord = x[0] if self.axis == "x" else x[1]
            y_coord = y[0] if self.axis == "x" else y[1]

            return x_coord == y_coord

        except (TypeError, IndexError) as e:
            logger.error("Error during weak identity check: %s", str(e))
            return False
