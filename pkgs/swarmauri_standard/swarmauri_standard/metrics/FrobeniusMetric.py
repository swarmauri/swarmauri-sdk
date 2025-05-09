from typing import Union, TypeVar, Sequence
import logging
import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.metrics.IMetric import IMetric

T = TypeVar("T", np.ndarray, Sequence, list)
logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "FrobeniusMetric")
class FrobeniusMetric(MetricBase):
    """
    Concrete implementation of the MetricBase class for computing the Frobenius metric
    between matrices. The Frobenius metric is defined as the square root of the sum
    of the squares of the differences between corresponding matrix elements.

    Inherits From:
        MetricBase: Base class providing template logic for metric computations
        IMetric (ABC): The interface for metric spaces
        ComponentBase: Base class for all components in the system

    Provides:
        Implementation of the distance method for Frobenius metric calculation
        Implementations for checking metric properties like non-negativity,
        identity, symmetry, and triangle inequality
    """

    def __init__(self):
        """
        Initializes the FrobeniusMetric instance.
        """
        super().__init__()
        logger.debug("FrobeniusMetric instance initialized")

    def distance(self, x: T, y: T) -> float:
        """
        Compute the Frobenius distance between two matrices.

        The Frobenius distance is defined as the square root of the sum of the squares
        of the differences between corresponding matrix elements.

        Args:
            x: T
                The first matrix
            y: T
                The second matrix

        Returns:
            float:
                The computed Frobenius distance between x and y

        Raises:
            ValueError:
                If the input matrices are not of compatible shapes
            TypeError:
                If the input matrices are of unsupported types
        """
        logger.debug("Starting Frobenius distance computation")

        try:
            # Ensure inputs are numpy arrays
            if not isinstance(x, np.ndarray):
                x = np.asarray(x)
            if not isinstance(y, np.ndarray):
                y = np.asarray(y)

            # Check if shapes match
            if x.shape != y.shape:
                raise ValueError("Input matrices must have the same shape")

            # Compute element-wise differences
            difference = x - y

            # Square the differences
            squared_diff = np.square(difference)

            # Sum the squared differences
            sum_of_squares = np.sum(squared_diff)

            # Take square root to get Frobenius norm
            distance = np.sqrt(sum_of_squares)

            logger.debug(f"Frobenius distance computed successfully: {distance}")
            return float(distance)

        except Exception as e:
            logger.error(f"Error computing Frobenius distance: {str(e)}")
            raise ValueError(f"Failed to compute Frobenius distance: {str(e)}")

    def distances(
        self, x: T, y_list: Union[T, Sequence[T]]
    ) -> Union[float, Sequence[float]]:
        """
        Compute the distance(s) between a matrix and one or more matrices.

        Args:
            x: T
                The reference matrix
            y_list: Union[T, Sequence[T]]
                Either a single matrix or a sequence of matrices

        Returns:
            Union[float, Sequence[float]]:
                - If y_list is a single matrix: Returns the distance as a float
                - If y_list is a sequence: Returns a sequence of distances

        Raises:
            ValueError:
                If the input matrices are not of compatible shapes
            TypeError:
                If the input matrices are of unsupported types
        """
        logger.debug("Starting multiple Frobenius distance computations")

        try:
            if isinstance(y_list, Sequence):
                return [self.distance(x, y) for y in y_list]
            else:
                return self.distance(x, y_list)

        except Exception as e:
            logger.error(f"Error computing multiple Frobenius distances: {str(e)}")
            raise ValueError(
                f"Failed to compute multiple Frobenius distances: {str(e)}"
            )

    def check_non_negativity(self, x: T, y: T) -> bool:
        """
        Verify the non-negativity axiom: d(x, y) ≥ 0.

        Args:
            x: T
                The first matrix
            y: T
                The second matrix

        Returns:
            bool:
                True if the non-negativity condition holds, False otherwise
        """
        logger.debug("Checking non-negativity of Frobenius metric")
        distance = self.distance(x, y)
        return distance >= 0.0

    def check_identity(self, x: T, y: T) -> bool:
        """
        Verify the identity of indiscernibles axiom: d(x, y) = 0 if and only if x = y.

        Args:
            x: T
                The first matrix
            y: T
                The second matrix

        Returns:
            bool:
                True if the identity condition holds, False otherwise
        """
        logger.debug("Checking identity of Frobenius metric")
        distance = self.distance(x, y)
        return distance == 0.0

    def check_symmetry(self, x: T, y: T) -> bool:
        """
        Verify the symmetry axiom: d(x, y) = d(y, x).

        Args:
            x: T
                The first matrix
            y: T
                The second matrix

        Returns:
            bool:
                True if the symmetry condition holds, False otherwise
        """
        logger.debug("Checking symmetry of Frobenius metric")
        distance_xy = self.distance(x, y)
        distance_yx = self.distance(y, x)
        return distance_xy == distance_yx

    def check_triangle_inequality(self, x: T, y: T, z: T) -> bool:
        """
        Verify the triangle inequality axiom: d(x, z) ≤ d(x, y) + d(y, z).

        Args:
            x: T
                The first matrix
            y: T
                The second matrix
            z: T
                The third matrix

        Returns:
            bool:
                True if the triangle inequality condition holds, False otherwise
        """
        logger.debug("Checking triangle inequality of Frobenius metric")

        distance_xz = self.distance(x, z)
        distance_xy = self.distance(x, y)
        distance_yz = self.distance(y, z)

        return distance_xz <= (distance_xy + distance_yz)
