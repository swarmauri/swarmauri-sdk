import logging
from typing import Union, Sequence, Optional, Literal, List
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_standard.swarmauri_standard.norms.L2EuclideanNorm import L2EuclideanNorm

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class EuclideanMetric(MetricBase):
    """
    Concrete implementation of the MetricBase class for computing the Euclidean distance.

    The Euclidean distance is the straight-line distance between two points in Euclidean space.
    It is calculated as the square root of the sum of the squared differences between corresponding
    elements of the vectors. This implementation provides the core functionality for distance
    computation while enforcing the metric properties.

    Inherits From:
        MetricBase: Base class for metric space implementations

    Attributes:
        type: Type identifier for the metric implementation
        resource: Type of resource this component represents
    """

    type: Literal["EuclideanMetric"] = "EuclideanMetric"
    resource: Optional[str] = "metric"

    def __init__(self):
        """
        Initialize the EuclideanMetric instance.

        Initializes the base class and sets up the L2 norm for distance calculations.
        """
        super().__init__()
        self.norm = L2EuclideanNorm()

    def distance(
        self, x: Union[Sequence, str, callable], y: Union[Sequence, str, callable]
    ) -> float:
        """
        Compute the Euclidean distance between two vectors.

        The computation follows the formula:
        d(x, y) = ||x - y||_2 = sqrt((x1 - y1)^2 + (x2 - y2)^2 + ... + (xn - yn)^2)

        Args:
            x: The first vector. Can be a sequence, string, or callable.
            y: The second vector. Can be a sequence, string, or callable.

        Returns:
            float: The computed Euclidean distance between x and y.

        Raises:
            ValueError: If the input vectors have different dimensions.
        """
        try:
            # Ensure both vectors are of the same dimension
            if len(x) != len(y):
                raise ValueError(
                    "Vectors must be of the same dimension for Euclidean distance"
                )

            # Compute the element-wise difference
            difference = [x_i - y_i for x_i, y_i in zip(x, y)]

            # Compute the L2 norm of the difference
            distance = self.norm.compute(difference)

            logger.info(f"Computed Euclidean distance: {distance}")
            return distance

        except Exception as e:
            logger.error(f"Failed to compute Euclidean distance: {str(e)}")
            raise

    def distances(
        self,
        x: Union[Sequence, str, callable],
        ys: List[Union[Sequence, str, callable]],
    ) -> List[float]:
        """
        Compute distances from a single point to multiple points.

        Args:
            x: The reference point. Can be a sequence, string, or callable.
            ys: List of points to compute distances to. Each can be a sequence, string, or callable.

        Returns:
            List[float]: List of distances from x to each point in ys.

        Raises:
            ValueError: If any input vector has different dimension than x.
        """
        try:
            distances = []
            for y in ys:
                distances.append(self.distance(x, y))

            logger.info(f"Computed distances: {distances}")
            return distances

        except Exception as e:
            logger.error(f"Failed to compute distances: {str(e)}")
            raise

    def check_non_negativity(
        self, x: Union[Sequence, str, callable], y: Union[Sequence, str, callable]
    ) -> Literal[True]:
        """
        Verify the non-negativity property: d(x, y) ≥ 0.

        Args:
            x: The first point. Can be a sequence, string, or callable.
            y: The second point. Can be a sequence, string, or callable.

        Returns:
            Literal[True]: True if the non-negativity property holds.

        Raises:
            AssertionError: If the non-negativity property is violated.
        """
        try:
            distance = self.distance(x, y)
            assert distance >= 0, "Non-negativity violated: Distance is negative"

            logger.info("Non-negativity property verified")
            return True

        except AssertionError as e:
            logger.error(f"Non-negativity check failed: {str(e)}")
            raise

    def check_identity(
        self, x: Union[Sequence, str, callable], y: Union[Sequence, str, callable]
    ) -> Literal[True]:
        """
        Verify the identity of indiscernibles property: d(x, y) = 0 if and only if x = y.

        Args:
            x: The first point. Can be a sequence, string, or callable.
            y: The second point. Can be a sequence, string, or callable.

        Returns:
            Literal[True]: True if the identity property holds.

        Raises:
            AssertionError: If the identity property is violated.
        """
        try:
            distance = self.distance(x, y)
            if distance != 0:
                assert x == y, (
                    "Identity violated: Distance is zero but vectors are not identical"
                )

            logger.info("Identity property verified")
            return True

        except AssertionError as e:
            logger.error(f"Identity check failed: {str(e)}")
            raise

    def check_symmetry(
        self, x: Union[Sequence, str, callable], y: Union[Sequence, str, callable]
    ) -> Literal[True]:
        """
        Verify the symmetry property: d(x, y) = d(y, x).

        Args:
            x: The first point. Can be a sequence, string, or callable.
            y: The second point. Can be a sequence, string, or callable.

        Returns:
            Literal[True]: True if the symmetry property holds.

        Raises:
            AssertionError: If the symmetry property is violated.
        """
        try:
            d_xy = self.distance(x, y)
            d_yx = self.distance(y, x)

            assert abs(d_xy - d_yx) < 1e-9, "Symmetry violated: d(x, y) != d(y, x)"

            logger.info("Symmetry property verified")
            return True

        except AssertionError as e:
            logger.error(f"Symmetry check failed: {str(e)}")
            raise

    def check_triangle_inequality(
        self,
        x: Union[Sequence, str, callable],
        y: Union[Sequence, str, callable],
        z: Union[Sequence, str, callable],
    ) -> Literal[True]:
        """
        Verify the triangle inequality property: d(x, z) ≤ d(x, y) + d(y, z).

        Args:
            x: The first point. Can be a sequence, string, or callable.
            y: The second point. Can be a sequence, string, or callable.
            z: The third point. Can be a sequence, string, or callable.

        Returns:
            Literal[True]: True if the triangle inequality property holds.

        Raises:
            AssertionError: If the triangle inequality is violated.
        """
        try:
            d_xz = self.distance(x, z)
            d_xy = self.distance(x, y)
            d_yz = self.distance(y, z)

            assert d_xz <= d_xy + d_yz, (
                "Triangle inequality violated: d(x, z) > d(x, y) + d(y, z)"
            )

            logger.info("Triangle inequality property verified")
            return True

        except AssertionError as e:
            logger.error(f"Triangle inequality check failed: {str(e)}")
            raise
