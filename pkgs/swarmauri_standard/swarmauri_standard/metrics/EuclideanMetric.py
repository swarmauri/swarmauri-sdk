from typing import Union, TypeVar, Sequence, Optional
import logging
import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.metrics.IMetric import IMetric

T = TypeVar("T", np.ndarray, Sequence, str)
S = TypeVar("S", int, float, bool, str)

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "EuclideanMetric")
class EuclideanMetric(MetricBase):
    """
    Provides a concrete implementation for computing the standard Euclidean distance
    between vectors. This class implements the L2 distance calculation and inherits
    from the MetricBase class.

    Inherits From:
        MetricBase: Base class for all metrics
        ComponentBase: Base class for all components
        IMetric: Interface for metric computations

    Provides:
        - Implementation of the distance method for L2 Euclidean distance
        - Implementations for all metric axioms (non-negativity, identity,
          symmetry, triangle inequality)
        - Logging functionality
    """

    resource: Optional[str] = "metric"

    def __init__(self):
        """
        Initialize the EuclideanMetric instance.

        Initializes the base class and sets up logging.
        """
        super().__init__()
        self.norm = L2EuclideanNorm()
        logger.debug("EuclideanMetric instance initialized")

    def distance(self, x: T, y: T) -> float:
        """
        Compute the Euclidean distance between two vectors.

        Args:
            x: T
                The first vector
            y: T
                The second vector

        Returns:
            float:
                The computed Euclidean distance between x and y

        Raises:
            ValueError:
                If input vectors have different dimensions
            TypeError:
                If inputs are not of compatible types
        """
        logger.debug("Starting Euclidean distance computation")

        try:
            # Convert inputs to numpy arrays if not already
            x = np.asarray(x)
            y = np.asarray(y)

            # Ensure vectors have the same dimension
            if x.shape != y.shape:
                raise ValueError("Input vectors must have the same dimensions")

            # Compute element-wise differences
            difference = x - y

            # Compute squared differences
            squared_diff = np.square(difference)

            # Sum of squares
            sum_of_squares = np.sum(squared_diff)

            # Square root gives the Euclidean distance
            distance = np.sqrt(sum_of_squares)

            logger.debug(f"Euclidean distance computed successfully: {distance}")
            return float(distance)

        except Exception as e:
            logger.error(f"Error computing Euclidean distance: {str(e)}")
            raise ValueError(f"Failed to compute Euclidean distance: {str(e)}")

    def distances(
        self, x: T, y_list: Union[T, Sequence[T]]
    ) -> Union[float, Sequence[float]]:
        """
        Compute the distance(s) between a vector and one or more vectors.

        Args:
            x: T
                The reference vector
            y_list: Union[T, Sequence[T]]
                Either a single vector or a sequence of vectors

        Returns:
            Union[float, Sequence[float]]:
                - If y_list is a single vector: Returns the distance as a float
                - If y_list is a sequence: Returns a sequence of distances

        Raises:
            ValueError:
                If input types are not compatible
            TypeError:
                If input types are invalid
        """
        logger.debug("Starting multiple distance computations")

        try:
            if isinstance(y_list, Sequence):
                return [self.distance(x, y) for y in y_list]
            else:
                return self.distance(x, y_list)

        except Exception as e:
            logger.error(f"Error computing multiple distances: {str(e)}")
            raise ValueError(f"Failed to compute distances: {str(e)}")

    def check_non_negativity(self, x: T, y: T) -> bool:
        """
        Verify the non-negativity axiom: d(x, y) ≥ 0.

        Args:
            x: T
                The first vector
            y: T
                The second vector

        Returns:
            bool:
                True if the non-negativity condition holds, False otherwise
        """
        logger.debug("Checking non-negativity axiom")
        distance = self.distance(x, y)
        return distance >= 0.0

    def check_identity(self, x: T, y: T) -> bool:
        """
        Verify the identity of indiscernibles axiom: d(x, y) = 0 if and only if x = y.

        Args:
            x: T
                The first vector
            y: T
                The second vector

        Returns:
            bool:
                True if the identity condition holds, False otherwise
        """
        logger.debug("Checking identity axiom")
        distance = self.distance(x, y)
        return distance == 0.0 if (x == y).all() else False

    def check_symmetry(self, x: T, y: T) -> bool:
        """
        Verify the symmetry axiom: d(x, y) = d(y, x).

        Args:
            x: T
                The first vector
            y: T
                The second vector

        Returns:
            bool:
                True if the symmetry condition holds, False otherwise
        """
        logger.debug("Checking symmetry axiom")
        d_xy = self.distance(x, y)
        d_yx = self.distance(y, x)
        return np.isclose(d_xy, d_yx)

    def check_triangle_inequality(self, x: T, y: T, z: T) -> bool:
        """
        Verify the triangle inequality axiom: d(x, z) ≤ d(x, y) + d(y, z).

        Args:
            x: T
                The first vector
            y: T
                The second vector
            z: T
                The third vector

        Returns:
            bool:
                True if the triangle inequality condition holds, False otherwise
        """
        logger.debug("Checking triangle inequality axiom")
        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)
        return d_xz <= (d_xy + d_yz)
