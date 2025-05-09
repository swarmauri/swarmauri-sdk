from typing import Union, TypeVar, Optional
import logging
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.metrics.IMetric import IMetric

T = TypeVar('T', int, float)

@ComponentBase.register_type(MetricBase, "AbsoluteValueMetric")
class AbsoluteValueMetric(MetricBase):
    """
    Provides a concrete implementation of the MetricBase class for computing
    the absolute difference between real numbers.

    Inherits From:
        MetricBase: The base class providing template logic for metric spaces.
        ComponentBase: Base class for all components in the system.
        IMetric: Interface for metric spaces.

    Provides:
        Implementation of the L1 metric (absolute value) for real numbers.
        Includes methods for computing distances and verifying metric axioms.
    """
    type: Literal["AbsoluteValueMetric"] = "AbsoluteValueMetric"
    resource: Optional[str] = Field(default="METRIC")

    def __init__(self):
        """
        Initialize the AbsoluteValueMetric instance.

        Sets up logging and initializes the base class.
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.debug("AbsoluteValueMetric instance initialized")

    def distance(self, x: T, y: T) -> float:
        """
        Compute the absolute difference between two real numbers.

        Args:
            x: T
                The first real number
            y: T
                The second real number

        Returns:
            float:
                The absolute difference between x and y

        Raises:
            ValueError:
                If either x or y is not a real number
        """
        self.logger.debug("Computing absolute difference between %s and %s", x, y)
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise ValueError("Inputs must be real numbers")
        return abs(x - y)

    def distances(self, x: T, y_list: Union[T, Sequence[T]]) -> Union[float, Sequence[float]]:
        """
        Compute the absolute differences between a reference point and one or more points.

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
            ValueError:
                If any input is not a real number
        """
        self.logger.debug("Computing distances from %s to %s", x, y_list)
        if isinstance(y_list, Sequence):
            return [abs(x - y) for y in y_list]
        return abs(x - y_list)

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
        """
        self.logger.debug("Checking non-negativity for points %s and %s", x, y)
        return self.distance(x, y) >= 0

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
        """
        self.logger.debug("Checking identity for points %s and %s", x, y)
        return self.distance(x, y) == 0 if x == y else (x == y if self.distance(x, y) == 0)

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
        """
        self.logger.debug("Checking symmetry for points %s and %s", x, y)
        return self.distance(x, y) == self.distance(y, x)

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
        """
        self.logger.debug("Checking triangle inequality for points %s, %s, %s", x, y, z)
        return self.distance(x, z) <= self.distance(x, y) + self.distance(y, z)