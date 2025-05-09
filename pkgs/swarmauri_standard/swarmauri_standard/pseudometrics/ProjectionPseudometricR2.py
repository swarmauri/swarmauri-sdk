from typing import Union, Sequence, List, Any
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.pseudometrics import PseudometricBase
import logging

logger = logging.getLogger(__name__)

class ProjectionPseudometricR2(PseudometricBase):
    """
    A pseudometric that projects 2D vectors onto a specified axis (x or y) and measures the distance based on the projection.

    This class implements a pseudometric by projecting 2D points onto either the x or y axis and then computing the distance between these projections. The projection axis can be specified during initialization.

    Inherits:
        PseudometricBase: Base class for pseudometrics

    Attributes:
        projection_axis: str
            Specifies which coordinate to use for projection. Can be 'x' or 'y'
    """
    resource: str = ResourceTypes.PSEUDOMETRIC.value

    def __init__(self, projection_axis: str = 'x'):
        """
        Initializes the ProjectionPseudometricR2 with the specified projection axis.

        Args:
            projection_axis: str
                The axis to project onto ('x' or 'y'). Defaults to 'x'

        Raises:
            ValueError: If projection_axis is not 'x' or 'y'
        """
        super().__init__()
        if projection_axis not in ['x', 'y']:
            raise ValueError("projection_axis must be either 'x' or 'y'")

        self.projection_axis = projection_axis
        logger.debug(f"Initialized ProjectionPseudometricR2 with projection_axis: {self.projection_axis}")

    def distance(self, x: Union[Sequence, Any], y: Union[Sequence, Any]) -> float:
        """
        Computes the pseudometric distance between two 2D points based on the projected coordinate.

        Args:
            x: Union[Sequence, Any]
                The first 2D point or vector
            y: Union[Sequence, Any]
                The second 2D point or vector

        Returns:
            float: The absolute difference between the projected coordinates

        Raises:
            ValueError: If inputs are not valid 2D points
        """
        try:
            x_coord = x[0] if self.projection_axis == 'x' else x[1]
            y_coord = y[0] if self.projection_axis == 'x' else y[1]
        except (TypeError, IndexError):
            logger.error("Invalid input: inputs must be 2D points")
            raise ValueError("Inputs must be 2D points")

        return abs(float(x_coord) - float(y_coord))

    def distances(self, xs: Sequence[Union[Sequence, Any]], ys: Sequence[Union[Sequence, Any]]) -> List[float]:
        """
        Computes pairwise pseudometric distances between two sequences of 2D points.

        Args:
            xs: Sequence[Union[Sequence, Any]]
                The first sequence of 2D points
            ys: Sequence[Union[Sequence, Any]]
                The second sequence of 2D points

        Returns:
            List[float]: A list of pairwise distances
        """
        return [self.distance(x, y) for x, y in zip(xs, ys)]

# Example usage
if __name__ == "__main__":
    # Example 1: Using default x-axis projection
    pm = ProjectionPseudometricR2()
    dist = pm.distance((1, 2), (3, 4))
    print(f"Distance on x-axis: {dist}")

    # Example 2: Using y-axis projection
    pm_y = ProjectionPseudometricR2(projection_axis='y')
    dist_y = pm_y.distance((1, 2), (3, 4))
    print(f"Distance on y-axis: {dist_y}")

    # Example 3: Batch distance calculation
    points = [(1, 2), (3, 4), (5, 6)]
    distances = pm(distances=points, points=points)
    print(f"Pairwise distances: {distances}")