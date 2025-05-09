from typing import Any, Sequence, TypeVar, Union, Optional
import logging
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase

T = TypeVar("T", Sequence, str)
logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "HammingMetric")
class HammingMetric(MetricBase):
    """
    Implements the Hamming metric, which calculates the number of positions
    at which the corresponding symbols are different.

    Inherits From:
        MetricBase: Base class for metrics implementing the IMetric interface

    Provides:
        - Implementation of the Hamming distance for binary or categorical vectors
        - Compliance with the metric axioms
        - Logging functionality
        - Comprehensive error handling
    """

    resource: Optional[str] = "metric"

    def __init__(self):
        """
        Initialize the HammingMetric instance.

        Initializes the base class and sets up logging.
        """
        super().__init__()
        logger.debug("HammingMetric instance initialized")

    def distance(self, x: T, y: T) -> float:
        """
        Compute the Hamming distance between two sequences.

        Args:
            x: T
                The first sequence
            y: T
                The second sequence

        Returns:
            float:
                The Hamming distance between x and y

        Raises:
            ValueError:
                If the input sequences are of different lengths
            TypeError:
                If the input types are incompatible
        """
        if len(x) != len(y):
            raise ValueError("Input sequences must be of the same length")

        # Count mismatched positions
        mismatches = sum(1 for a, b in zip(x, y) if a != b)
        logger.debug(f"Calculated Hamming distance: {mismatches}")
        return float(mismatches)

    def distances(
        self, x: T, y_list: Union[T, Sequence[T]]
    ) -> Union[float, Sequence[float]]:
        """
        Compute the Hamming distances from a reference sequence to one or more sequences.

        Args:
            x: T
                The reference sequence
            y_list: Union[T, Sequence[T]]
                Either a single sequence or a list of sequences

        Returns:
            Union[float, Sequence[float]]:
                - If y_list is a single sequence: Returns the distance as a float
                - If y_list is a sequence: Returns a list of distances

        Raises:
            ValueError:
                If any input sequence has different length than x
            TypeError:
                If the input types are incompatible
        """
        if isinstance(y_list, Sequence) and not isinstance(y_list, (str, bytes)):
            return [self.distance(x, y) for y in y_list]
        else:
            return self.distance(x, y_list)

    def check_non_negativity(self, x: T, y: T) -> bool:
        """
        Verify the non-negativity axiom: d(x, y) ≥ 0.

        Args:
            x: T
                The first sequence
            y: T
                The second sequence

        Returns:
            bool:
                True if the non-negativity condition holds, False otherwise

        Raises:
            ValueError:
                If the distance computation fails
        """
        distance = self.distance(x, y)
        return distance >= 0

    def check_identity(self, x: T, y: T) -> bool:
        """
        Verify the identity of indiscernibles axiom: d(x, y) = 0 if and only if x = y.

        Args:
            x: T
                The first sequence
            y: T
                The second sequence

        Returns:
            bool:
                True if the identity condition holds, False otherwise

        Raises:
            ValueError:
                If the distance computation fails
        """
        return self.distance(x, y) == 0

    def check_symmetry(self, x: T, y: T) -> bool:
        """
        Verify the symmetry axiom: d(x, y) = d(y, x).

        Args:
            x: T
                The first sequence
            y: T
                The second sequence

        Returns:
            bool:
                True if the symmetry condition holds, False otherwise

        Raises:
            ValueError:
                If the distance computation fails
        """
        return self.distance(x, y) == self.distance(y, x)

    def check_triangle_inequality(self, x: T, y: T, z: T) -> bool:
        """
        Verify the triangle inequality axiom: d(x, z) ≤ d(x, y) + d(y, z).

        Args:
            x: T
                The first sequence
            y: T
                The second sequence
            z: T
                The third sequence

        Returns:
            bool:
                True if the triangle inequality condition holds, False otherwise

        Raises:
            ValueError:
                If the distance computation fails
        """
        d_xz = self.distance(x, z)
        d_xy = self.distance(x, y)
        d_yz = self.distance(y, z)
        return d_xz <= d_xy + d_yz
