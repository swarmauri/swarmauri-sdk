from typing import Union, List, Optional
import logging
import numpy as np

from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.metrics.IMetric import IMetric
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

logger = logging.getLogger(__name__)


@MetricBase.register_type(MetricBase, "FrobeniusMetric")
class FrobeniusMetric(MetricBase, IMetric):
    """
    A class implementing the Frobenius metric for matrix distance calculations.

    Inherits from:
        MetricBase: Base class providing template logic for metric computations.
        IMetric: Interface defining the core metric functionality.

    Attributes:
        type: String identifier for the metric type.

    Methods:
        distance: Computes the Frobenius distance between two matrices.
        distances: Computes pairwise distances between two lists of matrices.
        check_non_negativity: Verifies the non-negativity axiom.
        check_identity: Verifies the identity of indiscernibles axiom.
        check_symmetry: Verifies the symmetry axiom.
        check_triangle_inequality: Verifies the triangle inequality axiom.
    """

    type: Literal["FrobeniusMetric"] = "FrobeniusMetric"

    def distance(
        self,
        x: Union[IVector, IMatrix, np.ndarray],
        y: Union[IVector, IMatrix, np.ndarray],
    ) -> float:
        """
        Computes the Frobenius distance between two matrices.

        The Frobenius distance is the square root of the sum of squared differences
        between corresponding matrix elements.

        Args:
            x: First matrix
            y: Second matrix

        Returns:
            float: The Frobenius distance between x and y

        Raises:
            ValueError: If the input matrices are not of the same shape
            TypeError: If the input matrices are not of a supported type
        """
        logger.debug("Calculating Frobenius distance between two matrices")

        # Ensure inputs are numpy arrays
        if not isinstance(x, (np.ndarray, IMatrix, IVector)):
            raise TypeError("Unsupported type for x")
        if not isinstance(y, (np.ndarray, IMatrix, IVector)):
            raise TypeError("Unsupported type for y")

        # Convert to numpy arrays if they're not already
        x = np.asarray(x)
        y = np.asarray(y)

        # Check if the matrices have the same shape
        if x.shape != y.shape:
            raise ValueError(
                "Matrices must have the same shape for Frobenius distance calculation"
            )

        # Calculate the element-wise difference
        difference = x - y

        # Compute the Frobenius norm (sqrt of sum of squares)
        try:
            distance = np.linalg.norm(difference)
        except ValueError as e:
            logger.error(f"Error calculating Frobenius distance: {str(e)}")
            raise ValueError("Failed to compute Frobenius distance")

        return distance

    def distances(
        self,
        xs: List[Union[IVector, IMatrix, np.ndarray]],
        ys: List[Union[IVector, IMatrix, np.ndarray]],
    ) -> List[List[float]]:
        """
        Computes pairwise Frobenius distances between two lists of matrices.

        Args:
            xs: First list of matrices
            ys: Second list of matrices

        Returns:
            List[List[float]]: Matrix of pairwise distances between xs and ys

        Raises:
            ValueError: If the input lists are not of compatible lengths
            TypeError: If any element is not a supported matrix type
        """
        logger.debug(
            f"Calculating pairwise Frobenius distances between {len(xs)} and {len(ys)} matrices"
        )

        if len(xs) != len(ys):
            raise ValueError("Input lists must be of the same length")

        # Initialize the distance matrix
        distance_matrix = []

        for x, y in zip(xs, ys):
            distance = self.distance(x, y)
            distance_matrix.append([distance])

        return distance_matrix

    def check_non_negativity(
        self,
        x: Union[IVector, IMatrix, np.ndarray],
        y: Union[IVector, IMatrix, np.ndarray],
    ) -> None:
        """
        Verifies the non-negativity axiom for the Frobenius metric.

        Args:
            x: First matrix
            y: Second matrix

        Raises:
            ValueError: If the distance is negative
        """
        logger.debug("Checking non-negativity axiom for Frobenius metric")

        distance = self.distance(x, y)
        if distance < 0:
            raise ValueError(f"Frobenius distance cannot be negative, got {distance}")

    def check_identity(
        self,
        x: Union[IVector, IMatrix, np.ndarray],
        y: Union[IVector, IMatrix, np.ndarray],
    ) -> None:
        """
        Verifies the identity of indiscernibles axiom for the Frobenius metric.

        Args:
            x: First matrix
            y: Second matrix

        Raises:
            ValueError: If x != y but distance is 0 or x == y but distance != 0
        """
        logger.debug("Checking identity of indiscernibles axiom for Frobenius metric")

        distance = self.distance(x, y)
        if (x == y and distance != 0) or (x != y and distance == 0):
            raise ValueError("Identity of indiscernibles axiom violated")

    def check_symmetry(
        self,
        x: Union[IVector, IMatrix, np.ndarray],
        y: Union[IVector, IMatrix, np.ndarray],
    ) -> None:
        """
        Verifies the symmetry axiom for the Frobenius metric.

        Args:
            x: First matrix
            y: Second matrix

        Raises:
            ValueError: If d(x,y) != d(y,x)
        """
        logger.debug("Checking symmetry axiom for Frobenius metric")

        distance_xy = self.distance(x, y)
        distance_yx = self.distance(y, x)

        if not np.isclose(distance_xy, distance_yx):
            raise ValueError(
                f"Symmetry axiom violated: d(x,y)={distance_xy}, d(y,x)={distance_yx}"
            )

    def check_triangle_inequality(
        self,
        x: Union[IVector, IMatrix, np.ndarray],
        y: Union[IVector, IMatrix, np.ndarray],
        z: Union[IVector, IMatrix, np.ndarray],
    ) -> None:
        """
        Verifies the triangle inequality axiom for the Frobenius metric.

        Args:
            x: First matrix
            y: Second matrix
            z: Third matrix

        Raises:
            ValueError: If d(x,z) > d(x,y) + d(y,z)
        """
        logger.debug("Checking triangle inequality axiom for Frobenius metric")

        distance_xz = self.distance(x, z)
        distance_xy = self.distance(x, y)
        distance_yz = self.distance(y, z)

        if distance_xz > distance_xy + distance_yz:
            raise ValueError(
                f"Triangle inequality violated: d(x,z)={distance_xz}, d(x,y)+d(y,z)={distance_xy + distance_yz}"
            )

    def __str__(self) -> str:
        """
        Returns a string representation of the FrobeniusMetric instance.
        """
        return f"FrobeniusMetric()"

    def __repr__(self) -> str:
        """
        Returns a string representation of the FrobeniusMetric instance.
        """
        return f"FrobeniusMetric()"
