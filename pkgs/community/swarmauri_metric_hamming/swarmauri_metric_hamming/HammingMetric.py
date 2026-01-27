"""Implementation of the classic Hamming distance for Swarmauri metrics."""

from __future__ import annotations

from typing import List, Literal, Sequence, Tuple, Union, cast

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.metrics.IMetric import MetricInput, MetricInputCollection
from swarmauri_core.vectors.IVector import IVector


def _is_scalar_sequence(value: Sequence[object]) -> bool:
    """Return ``True`` if *value* behaves like a single metric input."""

    if isinstance(value, (str, bytes)):
        return True

    if not value:
        return True

    first = value[0]
    return not isinstance(first, (Sequence, dict, np.ndarray)) or isinstance(
        first, (str, bytes)
    )


def _flatten_once(value: Sequence[object]) -> List[object]:
    """Flatten a sequence by one dimension."""

    flattened: List[object] = []
    for item in value:
        if isinstance(item, Sequence) and not isinstance(item, (str, bytes)):
            flattened.extend(list(item))
        else:
            flattened.append(item)
    return flattened


@ComponentBase.register_type(MetricBase, "HammingMetric")
class HammingMetric(MetricBase):
    """Concrete implementation of the Hamming distance."""

    type: Literal["HammingMetric"] = "HammingMetric"

    def _normalise_single(self, value: MetricInput) -> List[object]:
        """Convert a ``MetricInput`` into a one-dimensional Python list."""

        if isinstance(value, (int, float)):
            return [value]

        if isinstance(value, (str, bytes)):
            return list(value.decode() if isinstance(value, bytes) else value)

        if isinstance(value, dict):
            return list(value.values())

        if isinstance(value, np.ndarray):
            return value.flatten().tolist()

        if isinstance(value, IMatrix):
            return _flatten_once(cast(Sequence[object], value.tolist()))

        if isinstance(value, IVector):
            if hasattr(value, "tolist"):
                result = cast(Sequence[object], value.tolist())
                return (
                    list(result)
                    if _is_scalar_sequence(result)
                    else _flatten_once(result)
                )
            return list(value)  # type: ignore[arg-type]

        if hasattr(value, "tolist"):
            as_list = cast(Sequence[object], value.tolist())
            return (
                list(as_list)
                if _is_scalar_sequence(as_list)
                else _flatten_once(as_list)
            )

        if isinstance(value, Sequence):
            return list(value) if _is_scalar_sequence(value) else _flatten_once(value)

        raise TypeError(f"Unsupported metric input type: {type(value)!r}")

    def _normalise_collection(
        self, values: Union[MetricInput, MetricInputCollection]
    ) -> List[List[object]]:
        """Normalise a metric input or collection into a list of vectors."""

        if isinstance(values, np.ndarray) and values.ndim > 1:
            return [row.flatten().tolist() for row in values]

        if isinstance(values, Sequence) and not isinstance(values, (str, bytes)):
            if values and not _is_scalar_sequence(values):
                return [self._normalise_single(item) for item in values]  # type: ignore[arg-type]

        return [self._normalise_single(cast(MetricInput, values))]

    def normalise(self, value: MetricInput) -> List[object]:
        """Expose the internal normalisation logic for downstream components."""

        return self._normalise_single(value)

    def _validate_pair(
        self, x: List[object], y: List[object]
    ) -> Tuple[List[object], List[object]]:
        if len(x) != len(y):
            raise ValueError("Hamming distance requires inputs of equal length")
        return x, y

    def distance(self, x: MetricInput, y: MetricInput) -> float:
        left, right = self._validate_pair(
            self._normalise_single(x), self._normalise_single(y)
        )
        return float(sum(1 for a, b in zip(left, right) if a != b))

    def distances(
        self,
        x: Union[MetricInput, MetricInputCollection],
        y: Union[MetricInput, MetricInputCollection],
    ) -> Union[List[float], List[List[float]]]:
        left_vectors = self._normalise_collection(x)
        right_vectors = self._normalise_collection(y)

        if len(left_vectors) == 1 and len(right_vectors) == 1:
            return [self.distance(left_vectors[0], right_vectors[0])]  # type: ignore[arg-type]

        results: List[List[float]] = []
        for left in left_vectors:
            row: List[float] = []
            for right in right_vectors:
                row.append(self.distance(left, right))  # type: ignore[arg-type]
            results.append(row)
        return results

    def check_non_negativity(self, x: MetricInput, y: MetricInput) -> bool:
        return self.distance(x, y) >= 0

    def check_identity_of_indiscernibles(self, x: MetricInput, y: MetricInput) -> bool:
        left, right = self._normalise_single(x), self._normalise_single(y)
        distance = self.distance(left, right)
        return distance == 0 if left == right else distance > 0

    def check_symmetry(self, x: MetricInput, y: MetricInput) -> bool:
        return self.distance(x, y) == self.distance(y, x)

    def check_triangle_inequality(
        self, x: MetricInput, y: MetricInput, z: MetricInput
    ) -> bool:
        return self.distance(x, z) <= self.distance(x, y) + self.distance(y, z)


__all__ = ["HammingMetric"]
