from typing import Union, List, Literal, Optional
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "HammingMetric")
class HammingMetric(MetricBase):
    """
    Implementation of the Hamming metric. This class provides a way to compute
    the Hamming distance between two sequences. The Hamming distance is the
    number of positions at which the corresponding symbols are different.

    Inherits from MetricBase and implements the required distance
    computation methods while satisfying the metric axioms.
    """

    type: Literal["HammingMetric"] = "HammingMetric"

    def distance(self, x: Union[List, str, bytes], y: Union[List, str, bytes]) -> float:
        """
        Compute the Hamming distance between two sequences.

        Args:
            x: The first sequence. Can be a list, string, or bytes object.
            y: The second sequence. Can be a list, string, or bytes object.

        Returns:
            float: The Hamming distance between x and y.

        Raises:
            ValueError: If the input sequences are not of the same length.
        """
        logger.debug("Computing Hamming distance between two sequences")

        if len(x) != len(y):
            raise ValueError("Input sequences must be of the same length")

        # Count mismatched positions
        mismatches = sum(1 for a, b in zip(x, y) if a != b)

        return float(mismatches)

    def distances(
        self, x: Union[List, str, bytes], ys: List[Union[List, str, bytes]]
    ) -> List[float]:
        """
        Compute the Hamming distances from a single point to multiple points.

        Args:
            x: The reference sequence. Can be a list, string, or bytes object.
            ys: List of sequences to compute distances to.

        Returns:
            List[float]: List of Hamming distances from x to each sequence in ys.
        """
        logger.debug("Computing multiple Hamming distances from a reference sequence")

        return [self.distance(x, y) for y in ys]

    def check_non_negativity(
        self, x: Union[List, str, bytes], y: Union[List, str, bytes]
    ) -> Literal[True]:
        """
        Verify the non-negativity property: d(x, y) ≥ 0.

        Args:
            x: The first sequence. Can be a list, string, or bytes object.
            y: The second sequence. Can be a list, string, or bytes object.

        Returns:
            Literal[True]: Always True for Hamming metric as distances are non-negative.
        """
        logger.debug("Verifying non-negativity property")
        return True

    def check_identity(
        self, x: Union[List, str, bytes], y: Union[List, str, bytes]
    ) -> Literal[True]:
        """
        Verify the identity property: d(x, y) = 0 if and only if x = y.

        Args:
            x: The first sequence. Can be a list, string, or bytes object.
            y: The second sequence. Can be a list, string, or bytes object.

        Returns:
            Literal[True]: True if x and y are identical, False otherwise.
        """
        logger.debug("Verifying identity property")
        return self.distance(x, y) == 0.0

    def check_symmetry(
        self, x: Union[List, str, bytes], y: Union[List, str, bytes]
    ) -> Literal[True]:
        """
        Verify the symmetry property: d(x, y) = d(y, x).

        Args:
            x: The first sequence. Can be a list, string, or bytes object.
            y: The second sequence. Can be a list, string, or bytes object.

        Returns:
            Literal[True]: Always True as Hamming distance is symmetric.
        """
        logger.debug("Verifying symmetry property")
        return self.distance(x, y) == self.distance(y, x)

    def check_triangle_inequality(
        self,
        x: Union[List, str, bytes],
        y: Union[List, str, bytes],
        z: Union[List, str, bytes],
    ) -> Literal[True]:
        """
        Verify the triangle inequality property: d(x, z) ≤ d(x, y) + d(y, z).

        Args:
            x: The first sequence. Can be a list, string, or bytes object.
            y: The second sequence. Can be a list, string, or bytes object.
            z: The third sequence. Can be a list, string, or bytes object.

        Returns:
            Literal[True]: True if the triangle inequality holds.
        """
        logger.debug("Verifying triangle inequality property")

        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)

        return d_xz <= d_xy + d_yz
