from typing import Union, List, Sequence, float
import logging
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.metrics.IMetric import IMetric

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "AbsoluteValueMetric")
class AbsoluteValueMetric(MetricBase):
    """
    A class implementing the absolute value metric for real numbers.

    This class provides the concrete implementation for computing the absolute
    difference between two real numbers. It inherits from the MetricBase class
    and implements all required methods for metric computation.

    Inherits from:
        MetricBase: Base class providing template logic for metric computations.

    Attributes:
        type: Literal["AbsoluteValueMetric"] = "AbsoluteValueMetric"
            Type identifier for this metric class.

    Methods:
        distance: Computes the absolute difference between two scalars.
        distances: Computes pairwise absolute differences between two lists of scalars.
        check_non_negativity: Verifies the non-negativity axiom.
        check_identity: Verifies the identity of indiscernibles axiom.
        check_symmetry: Verifies the symmetry axiom.
        check_triangle_inequality: Verifies the triangle inequality axiom.
    """

    type: Literal["AbsoluteValueMetric"] = "AbsoluteValueMetric"

    def distance(self, x: Union[float, int], y: Union[float, int]) -> float:
        """
        Computes the absolute difference between two real numbers.

        Args:
            x: First scalar value
            y: Second scalar value

        Returns:
            float: The absolute difference between x and y

        Raises:
            TypeError: If inputs are not numeric scalars
        """
        logger.debug(f"Calculating absolute difference between {x} and {y}")

        # Ensure inputs are numeric
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise TypeError("Inputs must be numeric scalars")

        return float(abs(x - y))

    def distances(
        self, xs: List[Union[float, int]], ys: List[Union[float, int]]
    ) -> List[List[float]]:
        """
        Computes pairwise absolute differences between two lists of scalars.

        Args:
            xs: First list of scalar values
            ys: Second list of scalar values

        Returns:
            List[List[float]]: Matrix of pairwise absolute differences

        Raises:
            TypeError: If any input is not a numeric scalar
        """
        logger.debug(
            f"Calculating pairwise distances between {len(xs)} and {len(ys)} elements"
        )

        # Validate input types
        for x in xs:
            if not isinstance(x, (int, float)):
                raise TypeError("All elements in xs must be numeric scalars")
        for y in ys:
            if not isinstance(y, (int, float)):
                raise TypeError("All elements in ys must be numeric scalars")

        # Compute pairwise distances
        return [[float(abs(x - y)) for y in ys] for x in xs]

    def check_non_negativity(self, x: Union[float, int], y: Union[float, int]) -> None:
        """
        Verifies the non-negativity axiom: d(x,y) ≥ 0.

        Args:
            x: First scalar value
            y: Second scalar value

        Raises:
            ValueError: If the computed distance is negative
        """
        logger.debug("Checking non-negativity axiom")
        distance = self.distance(x, y)
        if distance < 0:
            raise ValueError(
                f"Non-negativity violated: distance({x}, {y}) = {distance}"
            )

    def check_identity(self, x: Union[float, int], y: Union[float, int]) -> None:
        """
        Verifies the identity of indiscernibles axiom: d(x,y) = 0 if and only if x = y.

        Args:
            x: First scalar value
            y: Second scalar value

        Raises:
            ValueError: If d(x,y) = 0 but x ≠ y, or d(x,y) ≠ 0 but x = y
        """
        logger.debug("Checking identity of indiscernibles axiom")
        distance = self.distance(x, y)
        if x == y and distance != 0:
            raise ValueError(
                f"Identity axiom violated: x == y but distance = {distance}"
            )
        if x != y and distance == 0:
            raise ValueError(
                f"Identity axiom violated: x != y but distance = {distance}"
            )

    def check_symmetry(self, x: Union[float, int], y: Union[float, int]) -> None:
        """
        Verifies the symmetry axiom: d(x,y) = d(y,x).

        Args:
            x: First scalar value
            y: Second scalar value

        Raises:
            ValueError: If d(x,y) ≠ d(y,x)
        """
        logger.debug("Checking symmetry axiom")
        d_xy = self.distance(x, y)
        d_yx = self.distance(y, x)
        if d_xy != d_yx:
            raise ValueError(
                f"Symmetry axiom violated: d({x}, {y}) = {d_xy} ≠ {d_yx} = d({y}, {x})"
            )

    def check_triangle_inequality(
        self, x: Union[float, int], y: Union[float, int], z: Union[float, int]
    ) -> None:
        """
        Verifies the triangle inequality axiom: d(x,z) ≤ d(x,y) + d(y,z).

        Args:
            x: First scalar value
            y: Second scalar value
            z: Third scalar value

        Raises:
            ValueError: If d(x,z) > d(x,y) + d(y,z)
        """
        logger.debug("Checking triangle inequality axiom")
        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)

        if d_xz > d_xy + d_yz:
            raise ValueError(f"Triangle inequality violated: {d_xz} > {d_xy} + {d_yz}")
