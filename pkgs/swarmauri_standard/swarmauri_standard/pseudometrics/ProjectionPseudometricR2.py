from typing import Callable, List, Literal, Sequence, TypeVar, Union, Tuple

import logging

import numpy as np
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.pseudometrics.PseudometricBase import PseudometricBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.vectors.IVector import IVector

# Set up logging
logger = logging.getLogger(__name__)

# Type variables
T = TypeVar("T")

# Type literals for IVector and IMatrix
VectorType = Literal[IVector]
MatrixType = Literal[IMatrix]


@ComponentBase.register_type(PseudometricBase, "ProjectionPseudometricR2")
class ProjectionPseudometricR2(PseudometricBase):
    """
    A pseudometric that measures distance via projection in ℝ².

    This pseudometric projects points onto a specified coordinate axis (x or y)
    and calculates the distance between their projections. Since points with
    different coordinates can have the same projection, this satisfies the
    pseudometric properties (allowing d(x,y)=0 for x≠y).

    Attributes
    ----------
    type : Literal["ProjectionPseudometricR2"]
        The type identifier for this pseudometric
    projection_axis : int
        The axis to project onto (0 for x-axis, 1 for y-axis)
    """

    type: Literal["ProjectionPseudometricR2"] = "ProjectionPseudometricR2"
    projection_axis: int = Field(default=0, ge=0, le=1)

    def __init__(self, projection_axis: int = 0, **kwargs):
        """
        Initialize the ProjectionPseudometricR2.

        Parameters
        ----------
        projection_axis : int, optional
            The axis to project onto (0 for x-axis, 1 for y-axis), by default 0

        Raises
        ------
        ValueError
            If projection_axis is not 0 or 1
        """
        if projection_axis not in [0, 1]:
            logger.error(
                f"Invalid projection axis: {projection_axis}. Must be 0 (x-axis) or 1 (y-axis)."
            )
            raise ValueError("Projection axis must be 0 (x-axis) or 1 (y-axis)")

        super().__init__(**kwargs, projection_axis=projection_axis)
        logger.debug(
            f"Initialized ProjectionPseudometricR2 with projection_axis={projection_axis}"
        )

    def _validate_and_extract_coordinates(
        self, point: Union[VectorType, MatrixType, Sequence[T], str, Callable]
    ) -> Tuple[float, float]:
        """
        Validate input as a 2D point and extract its coordinates.

        Parameters
        ----------
        point : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The input to validate and extract coordinates from

        Returns
        -------
        Tuple[float, float]
            The (x, y) coordinates of the point

        Raises
        ------
        TypeError
            If the input is not a valid 2D point representation
        ValueError
            If the input cannot be interpreted as a 2D point
        """
        try:
            if isinstance(point, (IVector, list, tuple, np.ndarray)):
                # Convert to numpy array for uniform handling
                point_array = np.asarray(point)

                # Check if it's a 2D point
                if point_array.size != 2:
                    raise ValueError(
                        f"Expected a 2D point, got {point_array.size} dimensions"
                    )

                # Flatten in case it's a 2x1 or 1x2 array
                point_array = point_array.flatten()
                return (float(point_array[0]), float(point_array[1]))

            elif isinstance(point, IMatrix):
                # Convert to numpy array
                point_array = np.asarray(point)

                # Check if it can be interpreted as a 2D point
                if point_array.size != 2:
                    raise ValueError(
                        f"Expected a matrix that can be interpreted as a 2D point, got shape {point_array.shape}"
                    )

                # Flatten to extract coordinates
                point_array = point_array.flatten()
                return (float(point_array[0]), float(point_array[1]))

            elif isinstance(point, str):
                # Try to parse as a comma-separated coordinate pair
                try:
                    parts = point.strip("()[]{}").split(",")
                    if len(parts) != 2:
                        raise ValueError(
                            f"Expected a string representing a 2D point (e.g., '1,2'), got {point}"
                        )

                    x = float(parts[0].strip())
                    y = float(parts[1].strip())
                    return (x, y)
                except Exception as e:
                    raise ValueError(f"Failed to parse string as 2D point: {str(e)}")

            elif callable(point):
                # Evaluate the callable at t=0 and t=1 to get x and y coordinates
                try:
                    x = float(point(0))
                    y = float(point(1))
                    return (x, y)
                except Exception as e:
                    raise ValueError(
                        f"Failed to evaluate callable as 2D point: {str(e)}"
                    )

            else:
                raise TypeError(f"Unsupported input type: {type(point)}")

        except Exception as e:
            logger.error(f"Error validating and extracting coordinates: {str(e)}")
            raise

    def distance(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
    ) -> float:
        """
        Calculate the projection pseudometric distance between two 2D points.

        The distance is calculated as the absolute difference between the projected
        coordinates on the specified axis.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The first 2D point
        y : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The second 2D point

        Returns
        -------
        float
            The projection pseudometric distance between x and y

        Raises
        ------
        TypeError
            If inputs are not valid 2D point representations
        ValueError
            If inputs cannot be interpreted as 2D points
        """
        logger.debug(f"Calculating projection distance between {x} and {y}")

        try:
            # Extract coordinates from both points
            x_coords = self._validate_and_extract_coordinates(x)
            y_coords = self._validate_and_extract_coordinates(y)

            # Calculate distance along the projection axis
            return abs(x_coords[self.projection_axis] - y_coords[self.projection_axis])

        except Exception as e:
            logger.error(f"Error calculating projection distance: {str(e)}")
            raise

    def distances(
        self,
        xs: Sequence[Union[VectorType, MatrixType, Sequence[T], str, Callable]],
        ys: Sequence[Union[VectorType, MatrixType, Sequence[T], str, Callable]],
    ) -> List[List[float]]:
        """
        Calculate the pairwise projection distances between two collections of 2D points.

        Parameters
        ----------
        xs : Sequence[Union[VectorType, MatrixType, Sequence[T], str, Callable]]
            The first collection of 2D points
        ys : Sequence[Union[VectorType, MatrixType, Sequence[T], str, Callable]]
            The second collection of 2D points

        Returns
        -------
        List[List[float]]
            A matrix of distances where distances[i][j] is the projection distance between xs[i] and ys[j]

        Raises
        ------
        TypeError
            If inputs contain invalid 2D point representations
        ValueError
            If inputs cannot be interpreted as 2D points
        """
        logger.debug(
            f"Calculating pairwise projection distances between {len(xs)} and {len(ys)} points"
        )

        try:
            # Pre-extract all coordinates for efficiency
            x_points = [self._validate_and_extract_coordinates(x) for x in xs]
            y_points = [self._validate_and_extract_coordinates(y) for y in ys]

            # Calculate the distance matrix
            result = []
            for x_point in x_points:
                row = []
                for y_point in y_points:
                    # Calculate distance along the projection axis
                    dist = abs(
                        x_point[self.projection_axis] - y_point[self.projection_axis]
                    )
                    row.append(dist)
                result.append(row)

            return result

        except Exception as e:
            logger.error(f"Error calculating pairwise projection distances: {str(e)}")
            raise

    def check_non_negativity(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
    ) -> bool:
        """
        Check if the projection pseudometric satisfies the non-negativity property.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The first 2D point
        y : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The second 2D point

        Returns
        -------
        bool
            True if d(x,y) ≥ 0, which is always the case for this pseudometric
        """
        try:
            # Calculate the distance
            dist = self.distance(x, y)

            # Check if it's non-negative
            return dist >= 0

        except Exception as e:
            logger.error(f"Error checking non-negativity: {str(e)}")
            raise

    def check_symmetry(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        tolerance: float = 1e-10,
    ) -> bool:
        """
        Check if the projection pseudometric satisfies the symmetry property.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The first 2D point
        y : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The second 2D point
        tolerance : float, optional
            The tolerance for floating-point comparisons, by default 1e-10

        Returns
        -------
        bool
            True if d(x,y) = d(y,x) within tolerance, which is always the case for this pseudometric
        """
        try:
            # Calculate distances in both directions
            dist_xy = self.distance(x, y)
            dist_yx = self.distance(y, x)

            # Check if they're equal within tolerance
            return abs(dist_xy - dist_yx) < tolerance

        except Exception as e:
            logger.error(f"Error checking symmetry: {str(e)}")
            raise

    def check_triangle_inequality(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        z: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        tolerance: float = 1e-10,
    ) -> bool:
        """
        Check if the projection pseudometric satisfies the triangle inequality.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The first 2D point
        y : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The second 2D point
        z : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The third 2D point
        tolerance : float, optional
            The tolerance for floating-point comparisons, by default 1e-10

        Returns
        -------
        bool
            True if d(x,z) ≤ d(x,y) + d(y,z) within tolerance, which is always the case for this pseudometric
        """
        try:
            # Calculate the three distances
            dist_xy = self.distance(x, y)
            dist_yz = self.distance(y, z)
            dist_xz = self.distance(x, z)

            # Check the triangle inequality
            return dist_xz <= dist_xy + dist_yz + tolerance

        except Exception as e:
            logger.error(f"Error checking triangle inequality: {str(e)}")
            raise

    def check_weak_identity(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
    ) -> bool:
        """
        Check if the projection pseudometric satisfies the weak identity property.

        In a pseudometric, d(x,y) = 0 is allowed even when x ≠ y. For the projection
        pseudometric, this happens when two points have the same coordinate on the
        projection axis but differ in the other coordinate.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The first 2D point
        y : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The second 2D point

        Returns
        -------
        bool
            True if the pseudometric correctly handles the weak identity property
        """
        try:
            # Extract coordinates
            x_coords = self._validate_and_extract_coordinates(x)
            y_coords = self._validate_and_extract_coordinates(y)

            # Calculate the distance
            dist = self.distance(x, y)

            # Check if points are different but have the same projection
            points_differ = x_coords != y_coords
            same_projection = (
                x_coords[self.projection_axis] == y_coords[self.projection_axis]
            )

            # If points differ but have same projection, distance should be 0
            if points_differ and same_projection:
                return abs(dist) < 1e-10

            # If points are the same, distance should be 0
            if not points_differ:
                return abs(dist) < 1e-10

            # If points differ and have different projections, distance should be > 0
            return dist > 0

        except Exception as e:
            logger.error(f"Error checking weak identity: {str(e)}")
            raise
