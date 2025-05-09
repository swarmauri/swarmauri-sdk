from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
import logging
from typing import Any, Union, Sequence, TypeVar

T = TypeVar("T", bound=Any)
S = TypeVar("S", int, float, bool, str)

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "DiscreteMetric")
class DiscreteMetric(MetricBase):
    """
    A basic binary metric implementation that distinguishes points based on their equality.

    This metric returns 1 if two points are different and 0 if they are the same.
    It works with any hashable type and provides a simple way to distinguish points.

    Inherits From:
        MetricBase: The base class for all metrics in the system.

    Provides:
        - Implementation of the distance calculation between points
        - Comprehensive logging for debugging purposes
        - Full compliance with the metric axioms
    """

    def __init__(self):
        """
        Initialize the DiscreteMetric instance.

        Initializes the base class and sets up logging.
        """
        super().__init__()
        logger.debug("DiscreteMetric instance initialized")

    def distance(self, x: T, y: T) -> float:
        """
        Compute the distance between two points.

        The distance is 0 if the points are identical and 1 otherwise.

        Args:
            x: T
                The first point to compare
            y: T
                The second point to compare

        Returns:
            float:
                0.0 if x and y are the same, 1.0 otherwise

        Raises:
            TypeError:
                If the input types are not supported
        """
        try:
            if x == y:
                logger.debug(f"Identical points: {x} and {y}, distance=0.0")
                return 0.0
            else:
                logger.debug(f"Distinct points: {x} and {y}, distance=1.0")
                return 1.0
        except TypeError as e:
            logger.error(f"Unsupported type comparison: {str(e)}")
            raise TypeError(f"Unsupported type comparison: {str(e)}")

    def distances(
        self, x: T, y_list: Union[T, Sequence[T]]
    ) -> Union[float, Sequence[float]]:
        """
        Compute the distance(s) between a point and one or more points.

        Args:
            x: T
                The reference point
            y_list: Union[T, Sequence[T]]
                Either a single point or a sequence of points

        Returns:
            Union[float, Sequence[float]]:
                - If y_list is a single point: Returns the distance as a float
                - If y_list is a sequence: Returns a sequence of distances

        Raises:
            TypeError:
                If the input types are not supported
        """
        try:
            if isinstance(y_list, Sequence):
                return [self.distance(x, y) for y in y_list]
            else:
                return self.distance(x, y_list)
        except TypeError as e:
            logger.error(f"Unsupported type comparison: {str(e)}")
            raise TypeError(f"Unsupported type comparison: {str(e)}")

    def check_non_negativity(self, x: T, y: T) -> bool:
        """
        Verify the non-negativity axiom: d(x, y) ≥ 0.

        Args:
            x: T
                The first point
            y: T
                The second point

        Returns:
            bool:
                True if the non-negativity condition holds, False otherwise

        Raises:
            ValueError:
                If the distance computation fails
        """
        try:
            distance = self.distance(x, y)
            if distance >= 0:
                logger.debug(
                    f"Non-negativity satisfied: {x} and {y}, distance={distance}"
                )
                return True
            else:
                logger.error(
                    f"Non-negativity violation: {x} and {y}, distance={distance}"
                )
                return False
        except Exception as e:
            logger.error(f"Non-negativity check failed: {str(e)}")
            raise ValueError(f"Non-negativity check failed: {str(e)}")

    def check_identity(self, x: T, y: T) -> bool:
        """
        Verify the identity of indiscernibles axiom: d(x, y) = 0 if and only if x = y.

        Args:
            x: T
                The first point
            y: T
                The second point

        Returns:
            bool:
                True if the identity condition holds, False otherwise

        Raises:
            ValueError:
                If the identity check fails
        """
        try:
            if x == y:
                logger.debug(f"Identity satisfied: {x} and {y} are identical")
                return True
            else:
                logger.debug(f"Identity satisfied: {x} and {y} are distinct")
                return self.distance(x, y) == 0.0
        except Exception as e:
            logger.error(f"Identity check failed: {str(e)}")
            raise ValueError(f"Identity check failed: {str(e)}")

    def check_symmetry(self, x: T, y: T) -> bool:
        """
        Verify the symmetry axiom: d(x, y) = d(y, x).

        Args:
            x: T
                The first point
            y: T
                The second point

        Returns:
            bool:
                True if the symmetry condition holds, False otherwise

        Raises:
            ValueError:
                If the symmetry check fails
        """
        try:
            d_xy = self.distance(x, y)
            d_yx = self.distance(y, x)
            if d_xy == d_yx:
                logger.debug(f"Symmetry satisfied: d({x}, {y}) = d({y}, {x}) = {d_xy}")
                return True
            else:
                logger.error(
                    f"Symmetry violation: d({x}, {y}) = {d_xy}, d({y}, {x}) = {d_yx}"
                )
                return False
        except Exception as e:
            logger.error(f"Symmetry check failed: {str(e)}")
            raise ValueError(f"Symmetry check failed: {str(e)}")

    def check_triangle_inequality(self, x: T, y: T, z: T) -> bool:
        """
        Verify the triangle inequality axiom: d(x, z) ≤ d(x, y) + d(y, z).

        Args:
            x: T
                The first point
            y: T
                The second point
            z: T
                The third point

        Returns:
            bool:
                True if the triangle inequality condition holds, False otherwise

        Raises:
            ValueError:
                If the triangle inequality check fails
        """
        try:
            d_xz = self.distance(x, z)
            d_xy = self.distance(x, y)
            d_yz = self.distance(y, z)
            if d_xz <= d_xy + d_yz:
                logger.debug(f"Triangle inequality satisfied: {d_xz} ≤ {d_xy} + {d_yz}")
                return True
            else:
                logger.error(f"Triangle inequality violation: {d_xz} > {d_xy} + {d_yz}")
                return False
        except Exception as e:
            logger.error(f"Triangle inequality check failed: {str(e)}")
            raise ValueError(f"Triangle inequality check failed: {str(e)}")
