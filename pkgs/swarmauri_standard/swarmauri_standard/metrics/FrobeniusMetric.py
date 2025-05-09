import logging
from typing import Union, List, Literal, Optional, Callable
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class FrobeniusMetric(MetricBase):
    """
    Concrete implementation of the MetricBase class for computing the Frobenius metric.

    The Frobenius metric calculates the distance between two matrices as the square root
    of the sum of the squares of their element-wise differences. This implementation
    provides the core functionality for computing the metric while adhering to the
    metric axioms.

    Inherits From:
        MetricBase: Base class for metric computations

    Attributes:
        type: Type identifier for the metric implementation
        resource: Type of resource this component represents
    """

    type: Literal["FrobeniusMetric"] = "FrobeniusMetric"
    resource: Optional[str] = "metric"

    def distance(
        self, x: Union[List, str, Callable], y: Union[List, str, Callable]
    ) -> float:
        """
        Compute the Frobenius distance between two matrices.

        The Frobenius distance is calculated as the square root of the sum
        of the squares of the differences between corresponding matrix elements.

        Args:
            x: The first matrix. Can be a list of lists, a string representation,
                or a callable that produces a matrix.
            y: The second matrix. Can be a list of lists, a string representation,
                or a callable that produces a matrix.

        Returns:
            float: The computed Frobenius distance between x and y.

        Raises:
            ValueError: If the input matrices cannot be processed or have different shapes
        """
        try:
            # Convert input to matrices if they are strings or callables
            if isinstance(x, str):
                x = [
                    list(map(float, row.strip().split()))
                    for row in x.strip().splitlines()
                ]
            elif callable(x):
                x = x()

            if isinstance(y, str):
                y = [
                    list(map(float, row.strip().split()))
                    for row in y.strip().splitlines()
                ]
            elif callable(y):
                y = y()

            # Check if shapes match
            if len(x) != len(y) or len(x[0]) != len(y[0]):
                raise ValueError("Matrices must have the same dimensions")

            # Calculate element-wise differences and sum of squares
            sum_squares = 0.0
            for i in range(len(x)):
                for j in range(len(x[0])):
                    diff = x[i][j] - y[i][j]
                    sum_squares += diff**2

            # Compute and return the square root of the sum of squares
            return sum_squares**0.5

        except Exception as e:
            logger.error(f"Failed to compute Frobenius distance: {str(e)}")
            raise ValueError("Invalid input for Frobenius distance computation")

    def distances(
        self, x: Union[List, str, Callable], ys: List[Union[List, str, Callable]]
    ) -> List[float]:
        """
        Compute distances from a single matrix to multiple matrices.

        Args:
            x: The reference matrix. Can be a list of lists, a string representation,
                or a callable that produces a matrix.
            ys: List of matrices to compute distances to. Each can be a list of lists,
                a string representation, or a callable that produces a matrix.

        Returns:
            List[float]: List of distances from x to each matrix in ys.

        Raises:
            ValueError: If any input matrix cannot be processed or has different dimensions than x
        """
        try:
            # Convert x to matrix if needed
            if isinstance(x, str):
                x = [
                    list(map(float, row.strip().split()))
                    for row in x.strip().splitlines()
                ]
            elif callable(x):
                x = x()

            distances = []
            for y in ys:
                if isinstance(y, str):
                    y = [
                        list(map(float, row.strip().split()))
                        for row in y.strip().splitlines()
                    ]
                elif callable(y):
                    y = y()

                if len(x) != len(y) or len(x[0]) != len(y[0]):
                    raise ValueError("All matrices must have the same dimensions")

                sum_squares = 0.0
                for i in range(len(x)):
                    for j in range(len(x[0])):
                        diff = x[i][j] - y[i][j]
                        sum_squares += diff**2
                distances.append(sum_squares**0.5)

            return distances

        except Exception as e:
            logger.error(f"Failed to compute distances: {str(e)}")
            raise ValueError("Failed to compute Frobenius distances")

    def check_non_negativity(
        self, x: Union[List, str, Callable], y: Union[List, str, Callable]
    ) -> Literal[True]:
        """
        Verify the non-negativity property: d(x, y) ≥ 0.

        Args:
            x: The first matrix. Can be a list of lists, a string representation,
                or a callable that produces a matrix.
            y: The second matrix. Can be a list of lists, a string representation,
                or a callable that produces a matrix.

        Returns:
            Literal[True]: True if the non-negativity property holds.

        Raises:
            AssertionError: If the non-negativity property is violated
        """
        distance = self.distance(x, y)
        assert distance >= 0, "Frobenius distance is negative - non-negativity violated"
        logger.info("Non-negativity property verified for Frobenius metric")
        return True

    def check_identity(
        self, x: Union[List, str, Callable], y: Union[List, str, Callable]
    ) -> Literal[True]:
        """
        Verify the identity of indiscernibles property: d(x, y) = 0 if and only if x = y.

        Args:
            x: The first matrix. Can be a list of lists, a string representation,
                or a callable that produces a matrix.
            y: The second matrix. Can be a list of lists, a string representation,
                or a callable that produces a matrix.

        Returns:
            Literal[True]: True if the identity property holds.

        Raises:
            AssertionError: If the identity property is violated
        """
        distance = self.distance(x, y)
        if distance != 0:
            logger.error(
                "Identity property violated: d(x, y) != 0 for identical matrices"
            )
        assert distance == 0, (
            "Identity property violated: d(x, y) != 0 for identical matrices"
        )
        logger.info("Identity property verified for Frobenius metric")
        return True

    def check_symmetry(
        self, x: Union[List, str, Callable], y: Union[List, str, Callable]
    ) -> Literal[True]:
        """
        Verify the symmetry property: d(x, y) = d(y, x).

        Args:
            x: The first matrix. Can be a list of lists, a string representation,
                or a callable that produces a matrix.
            y: The second matrix. Can be a list of lists, a string representation,
                or a callable that produces a matrix.

        Returns:
            Literal[True]: True if the symmetry property holds.

        Raises:
            AssertionError: If the symmetry property is violated
        """
        distance_xy = self.distance(x, y)
        distance_yx = self.distance(y, x)
        assert abs(distance_xy - distance_yx) < 1e-9, (
            "Symmetry property violated: d(x, y) != d(y, x)"
        )
        logger.info("Symmetry property verified for Frobenius metric")
        return True

    def check_triangle_inequality(
        self,
        x: Union[List, str, Callable],
        y: Union[List, str, Callable],
        z: Union[List, str, Callable],
    ) -> Literal[True]:
        """
        Verify the triangle inequality property: d(x, z) ≤ d(x, y) + d(y, z).

        Args:
            x: The first matrix. Can be a list of lists, a string representation,
                or a callable that produces a matrix.
            y: The second matrix. Can be a list of lists, a string representation,
                or a callable that produces a matrix.
            z: The third matrix. Can be a list of lists, a string representation,
                or a callable that produces a matrix.

        Returns:
            Literal[True]: True if the triangle inequality property holds.

        Raises:
            AssertionError: If the triangle inequality is violated
        """
        distance_xz = self.distance(x, z)
        distance_xy = self.distance(x, y)
        distance_yz = self.distance(y, z)
        assert distance_xz <= distance_xy + distance_yz, "Triangle inequality violated"
        logger.info("Triangle inequality property verified for Frobenius metric")
        return True
