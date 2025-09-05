import logging
from typing import List, Literal, Sequence, Union

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.metrics.IMetric import MetricInput, MetricInputCollection
from swarmauri_core.vectors.IVector import IVector

# Logger configuration
logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "HammingMetric")
class HammingMetric(MetricBase):
    """
    Hamming distance metric implementation.

    Hamming distance counts the number of positions at which two sequences differ.
    It is primarily used for binary/bitwise data and categorical vectors of equal length.

    Attributes
    ----------
    type : Literal["HammingMetric"]
        The type identifier for this metric
    """

    type: Literal["HammingMetric"] = "HammingMetric"

    def distance(self, x: MetricInput, y: MetricInput) -> float:
        """
        Calculate the Hamming distance between two sequences.

        The Hamming distance is the number of positions at which the corresponding
        elements of two sequences are different.

        Parameters
        ----------
        x : MetricInput
            First sequence
        y : MetricInput
            Second sequence

        Returns
        -------
        float
            The Hamming distance between x and y

        Raises
        ------
        ValueError
            If the sequences have different lengths
        TypeError
            If input types are not supported
        """
        logger.debug("Calculating Hamming distance between sequences")

        # Check if inputs are sequences
        if not isinstance(x, Sequence) or not isinstance(y, Sequence):
            raise TypeError("Inputs must be sequences")

        # Check if sequences have the same length
        if len(x) != len(y):
            raise ValueError(f"Sequences must have equal length: {len(x)} != {len(y)}")

        # Count positions where elements differ
        distance = sum(xi != yi for xi, yi in zip(x, y))

        logger.debug(f"Hamming distance: {distance}")
        return float(distance)

    def distances(
        self,
        x: Union[MetricInput, MetricInputCollection],
        y: Union[MetricInput, MetricInputCollection],
    ) -> Union[List[float], IVector, IMatrix]:
        """
        Calculate Hamming distances between collections of sequences.

        Parameters
        ----------
        x : Union[MetricInput, MetricInputCollection]
            First collection of sequences
        y : Union[MetricInput, MetricInputCollection]
            Second collection of sequences

        Returns
        -------
        Union[List[float], IVector, IMatrix]
            Matrix or vector of Hamming distances between sequences in x and y

        Raises
        ------
        ValueError
            If any pair of sequences have different lengths
        TypeError
            If input types are not supported
        """
        logger.debug("Calculating Hamming distances between collections")

        # Handle numpy arrays
        if isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
            # For 1D arrays (single sequences)
            if x.ndim == 1 and y.ndim == 1:
                if x.shape[0] != y.shape[0]:
                    raise ValueError(
                        f"Sequences must have equal length: {x.shape[0]} != {y.shape[0]}"
                    )
                return float(np.sum(x != y))

            # For 2D arrays (multiple sequences)
            elif x.ndim == 2 and y.ndim == 2:
                if x.shape[1] != y.shape[1]:
                    raise ValueError(
                        f"Sequences must have equal length: {x.shape[1]} != {y.shape[1]}"
                    )

                # Calculate distances between all pairs
                result = np.zeros((x.shape[0], y.shape[0]))
                for i in range(x.shape[0]):
                    for j in range(y.shape[0]):
                        result[i, j] = np.sum(x[i] != y[j])
                return result.tolist()

        # Handle lists and other sequence types
        try:
            # Check if x and y are collections of sequences
            if isinstance(x, Sequence) and isinstance(y, Sequence):
                # If both are single sequences
                if not isinstance(x[0], Sequence) and not isinstance(y[0], Sequence):
                    return [self.distance(x, y)]

                # If x is a collection and y is a single sequence
                elif isinstance(x[0], Sequence) and not isinstance(y[0], Sequence):
                    return [self.distance(xi, y) for xi in x]

                # If x is a single sequence and y is a collection
                elif not isinstance(x[0], Sequence) and isinstance(y[0], Sequence):
                    return [self.distance(x, yi) for yi in y]

                # If both are collections
                else:
                    return [[self.distance(xi, yi) for yi in y] for xi in x]
        except (TypeError, IndexError):
            raise TypeError("Inputs must be collections of sequences or sequences")

        raise TypeError("Unsupported input types")

    def check_non_negativity(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the Hamming metric satisfies the non-negativity axiom: d(x,y) ≥ 0.

        Hamming distance always satisfies this axiom as it counts differences,
        which cannot be negative.

        Parameters
        ----------
        x : MetricInput
            First sequence
        y : MetricInput
            Second sequence

        Returns
        -------
        bool
            True, as Hamming distance is always non-negative
        """
        logger.debug("Checking non-negativity axiom for Hamming distance")
        # Hamming distance is always non-negative as it counts differences
        return True

    def check_identity_of_indiscernibles(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the Hamming metric satisfies the identity of indiscernibles axiom:
        d(x,y) = 0 if and only if x = y.

        Parameters
        ----------
        x : MetricInput
            First sequence
        y : MetricInput
            Second sequence

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise
        """
        logger.debug("Checking identity of indiscernibles axiom for Hamming distance")

        # Calculate distance
        dist = self.distance(x, y)

        # Check if distance is 0 iff x equals y
        sequences_equal = x == y
        distance_zero = dist == 0

        return sequences_equal == distance_zero

    def check_symmetry(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the Hamming metric satisfies the symmetry axiom: d(x,y) = d(y,x).

        Parameters
        ----------
        x : MetricInput
            First sequence
        y : MetricInput
            Second sequence

        Returns
        -------
        bool
            True, as Hamming distance is always symmetric
        """
        logger.debug("Checking symmetry axiom for Hamming distance")

        # Calculate distances both ways
        dist_xy = self.distance(x, y)
        dist_yx = self.distance(y, x)

        # Check if they're equal
        return (
            abs(dist_xy - dist_yx) < 1e-10
        )  # Using small epsilon for float comparison

    def check_triangle_inequality(
        self, x: MetricInput, y: MetricInput, z: MetricInput
    ) -> bool:
        """
        Check if the Hamming metric satisfies the triangle inequality axiom:
        d(x,z) ≤ d(x,y) + d(y,z).

        Parameters
        ----------
        x : MetricInput
            First sequence
        y : MetricInput
            Second sequence
        z : MetricInput
            Third sequence

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise
        """
        logger.debug("Checking triangle inequality axiom for Hamming distance")

        # Calculate the three distances
        dist_xz = self.distance(x, z)
        dist_xy = self.distance(x, y)
        dist_yz = self.distance(y, z)

        # Check if triangle inequality holds
        return (
            dist_xz <= dist_xy + dist_yz + 1e-10
        )  # Small epsilon for float comparison
