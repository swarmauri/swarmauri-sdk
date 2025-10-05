"""Hamming distance metric packaged for the Swarmauri SDK."""

from __future__ import annotations

import logging
from typing import List, Literal, Sequence, Union

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.metrics.IMetric import MetricInput, MetricInputCollection
from swarmauri_core.vectors.IVector import IVector

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "HammingMetric")
class HammingMetric(MetricBase):
    """Concrete implementation of :class:`~swarmauri_core.metrics.IMetric`.

    The metric measures the Hamming distance between two equally-sized
    sequences.  Only the number of positions with unequal entries matters,
    making the metric especially convenient for binary codes such as the
    ``(7, 4)`` Hamming code implemented in :mod:`swarmauri_matrix_hamming74`.
    """

    type: Literal["HammingMetric"] = "HammingMetric"

    @staticmethod
    def _validate_sequences(x: Sequence[object], y: Sequence[object]) -> None:
        """Validate the provided sequences.

        Parameters
        ----------
        x, y:
            The sequences to compare.  Both must be indexable and have equal
            length.
        """

        if not isinstance(x, Sequence) or not isinstance(y, Sequence):
            raise TypeError("Inputs must be sequences")

        if len(x) != len(y):
            raise ValueError(f"Sequences must have equal length: {len(x)} != {len(y)}")

    def distance(self, x: MetricInput, y: MetricInput) -> float:
        """Return the Hamming distance between two sequences."""

        if not isinstance(x, Sequence) or not isinstance(y, Sequence):
            raise TypeError("Inputs must be sequences")

        self._validate_sequences(x, y)
        distance = sum(1 for xi, yi in zip(x, y) if xi != yi)
        logger.debug("Hamming distance between %s and %s: %s", x, y, distance)
        return float(distance)

    def distances(
        self,
        x: Union[MetricInput, MetricInputCollection],
        y: Union[MetricInput, MetricInputCollection],
    ) -> Union[List[float], IVector, IMatrix]:
        """Return Hamming distances for the provided collections."""

        if isinstance(x, Sequence) and isinstance(y, Sequence):
            if x and isinstance(x[0], Sequence):
                if y and isinstance(y[0], Sequence):
                    return [
                        [self.distance(xi, yi) for yi in y]  # type: ignore[arg-type]
                        for xi in x  # type: ignore[arg-type]
                    ]
                return [self.distance(xi, y) for xi in x]  # type: ignore[arg-type]

            if y and isinstance(y[0], Sequence):
                return [self.distance(x, yi) for yi in y]  # type: ignore[arg-type]

            return [self.distance(x, y)]

        raise TypeError("Inputs must be sequences or collections of sequences")

    def check_non_negativity(self, x: MetricInput, y: MetricInput) -> bool:
        """The Hamming metric is always non-negative."""

        return self.distance(x, y) >= 0

    def check_identity_of_indiscernibles(self, x: MetricInput, y: MetricInput) -> bool:
        """The distance is zero if and only if the sequences are identical."""

        return self.distance(x, y) == 0 if x == y else self.distance(x, y) > 0

    def check_symmetry(self, x: MetricInput, y: MetricInput) -> bool:
        """Return ``True`` if the symmetry axiom holds."""

        return self.distance(x, y) == self.distance(y, x)

    def check_triangle_inequality(
        self,
        x: MetricInput,
        y: MetricInput,
        z: MetricInput,
    ) -> bool:
        """Return ``True`` if the triangle inequality holds."""

        return self.distance(x, z) <= self.distance(x, y) + self.distance(y, z)

    def normalized_distance(self, x: MetricInput, y: MetricInput) -> float:
        """Return the Hamming distance normalised by the sequence length."""

        if not isinstance(x, Sequence) or not isinstance(y, Sequence):
            raise TypeError("Inputs must be sequences")

        self._validate_sequences(x, y)
        if not x:
            return 0.0
        return self.distance(x, y) / len(x)

    def weight(self, x: MetricInput) -> float:
        """Return the Hamming weight of a single sequence."""

        if not isinstance(x, Sequence):
            raise TypeError("Input must be a sequence")
        return float(sum(1 for xi in x if xi))
