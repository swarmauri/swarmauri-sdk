from typing import Union, List, Literal
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "AbsoluteValueMetric")
class AbsoluteValueMetric(MetricBase):
    """
    Implementation of the absolute value metric for real numbers.

    Inherits From:
        MetricBase: Base class for metric space implementations

    Attributes:
        type: Type identifier for this metric class
        resource: Type of resource this component represents
    """

    type: Literal["AbsoluteValueMetric"] = "AbsoluteValueMetric"
    resource: str = Field(default="metric")

    def __init__(self):
        """
        Initialize the AbsoluteValueMetric instance.
        """
        super().__init__()

    def distance(
        self, x: Union[int, float, str, Callable], y: Union[int, float, str, Callable]
    ) -> float:
        """
        Compute the distance between two points using absolute value.

        The distance is calculated as the absolute value of the difference between x and y.

        Args:
            x: The first point. Can be an int, float, string representation of a number, or a callable.
            y: The second point. Can be an int, float, string representation of a number, or a callable.

        Returns:
            float: The computed distance between x and y.

        Raises:
            ValueError: If the input cannot be converted to a numeric value
        """
        logger.debug("Computing absolute value distance")

        try:
            # Convert input to float values
            if isinstance(x, str):
                x_val = float(x)
            elif isinstance(x, Callable):
                x_val = float(x())
            else:
                x_val = float(x)

            if isinstance(y, str):
                y_val = float(y)
            elif isinstance(y, Callable):
                y_val = float(y())
            else:
                y_val = float(y)

            # Compute absolute difference
            distance = abs(x_val - y_val)
            logger.debug(f"Absolute value distance computed: {distance}")
            return distance

        except ValueError as e:
            logger.error(f"ValueError in distance computation: {str(e)}")
            raise ValueError(
                f"Invalid input for absolute value distance computation"
            ) from e
        except Exception as e:
            logger.error(f"Error in distance computation: {str(e)}")
            raise ValueError(f"Unexpected error during distance computation") from e

    def distances(
        self,
        x: Union[int, float, str, Callable],
        ys: List[Union[int, float, str, Callable]],
    ) -> List[float]:
        """
        Compute distances from a single point to multiple points.

        Args:
            x: The reference point. Can be an int, float, string representation of a number, or a callable.
            ys: List of points to compute distances to. Each can be an int, float, string representation of a number, or a callable.

        Returns:
            List[float]: List of distances from x to each point in ys.
        """
        logger.debug("Computing multiple absolute value distances")

        try:
            x_val = self._convert_to_float(x)
            return [abs(x_val - self._convert_to_float(y)) for y in ys]

        except Exception as e:
            logger.error(f"Error computing multiple distances: {str(e)}")
            raise ValueError("Failed to compute multiple distances") from e

    def _convert_to_float(self, value: Union[int, float, str, Callable]) -> float:
        """
        Helper method to convert input to a float value.

        Args:
            value: The input to convert. Can be an int, float, string representation of a number, or a callable.

        Returns:
            float: The converted float value.

        Raises:
            ValueError: If conversion fails
        """
        try:
            if isinstance(value, str):
                return float(value)
            elif isinstance(value, Callable):
                return float(value())
            else:
                return float(value)
        except Exception as e:
            raise ValueError(f"Failed to convert input to float: {str(e)}") from e

    def check_non_negativity(
        self, x: Union[int, float, str, Callable], y: Union[int, float, str, Callable]
    ) -> Literal[True]:
        """
        Verify the non-negativity property: d(x, y) ≥ 0.

        Args:
            x: The first point. Can be an int, float, string representation of a number, or a callable.
            y: The second point. Can be an int, float, string representation of a number, or a callable.

        Returns:
            Literal[True]: True if the non-negativity property holds.
        """
        logger.debug("Checking non-negativity property")

        distance = self.distance(x, y)
        assert distance >= 0, "Non-negativity violation: Distance is negative"
        logger.debug("Non-negativity property verified")
        return True

    def check_identity(
        self, x: Union[int, float, str, Callable], y: Union[int, float, str, Callable]
    ) -> Literal[True]:
        """
        Verify the identity of indiscernibles property: d(x, y) = 0 if and only if x = y.

        Args:
            x: The first point. Can be an int, float, string representation of a number, or a callable.
            y: The second point. Can be an int, float, string representation of a number, or a callable.

        Returns:
            Literal[True]: True if the identity property holds.
        """
        logger.debug("Checking identity property")

        distance = self.distance(x, y)
        if distance == 0:
            assert self._convert_to_float(x) == self._convert_to_float(y), (
                "Identity violation: Distance is zero but points are different"
            )
        else:
            assert distance != 0, (
                "Identity violation: Points are different but distance is zero"
            )

        logger.debug("Identity property verified")
        return True

    def check_symmetry(
        self, x: Union[int, float, str, Callable], y: Union[int, float, str, Callable]
    ) -> Literal[True]:
        """
        Verify the symmetry property: d(x, y) = d(y, x).

        Args:
            x: The first point. Can be an int, float, string representation of a number, or a callable.
            y: The second point. Can be an int, float, string representation of a number, or a callable.

        Returns:
            Literal[True]: True if the symmetry property holds.
        """
        logger.debug("Checking symmetry property")

        distance_xy = self.distance(x, y)
        distance_yx = self.distance(y, x)
        assert distance_xy == distance_yx, "Symmetry violation: d(x, y) != d(y, x)"
        logger.debug("Symmetry property verified")
        return True

    def check_triangle_inequality(
        self,
        x: Union[int, float, str, Callable],
        y: Union[int, float, str, Callable],
        z: Union[int, float, str, Callable],
    ) -> Literal[True]:
        """
        Verify the triangle inequality property: d(x, z) ≤ d(x, y) + d(y, z).

        Args:
            x: The first point. Can be an int, float, string representation of a number, or a callable.
            y: The second point. Can be an int, float, string representation of a number, or a callable.
            z: The third point. Can be an int, float, string representation of a number, or a callable.

        Returns:
            Literal[True]: True if the triangle inequality property holds.
        """
        logger.debug("Checking triangle inequality property")

        distance_xz = self.distance(x, z)
        distance_xy = self.distance(x, y)
        distance_yz = self.distance(y, z)

        assert distance_xz <= distance_xy + distance_yz, "Triangle inequality violation"
        logger.debug("Triangle inequality property verified")
        return True
