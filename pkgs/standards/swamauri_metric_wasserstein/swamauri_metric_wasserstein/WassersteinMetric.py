from itertools import chain
from math import inf, isfinite, isnan
from typing import List, Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_standard.vectors.Vector import Vector


@ComponentBase.register_type(MetricBase, "WassersteinMetric")
class WassersteinMetric(MetricBase):
    """Compute Wasserstein distance and derived similarity scores."""

    type: Literal["WassersteinMetric"] = "WassersteinMetric"

    @staticmethod
    def _validate_values(values_a: List[float], values_b: List[float]) -> None:
        """Validate Wasserstein input values before CDF iteration."""
        if not values_a or not values_b:
            raise ValueError("Wasserstein distance requires non-empty vectors.")

        all_values = chain(values_a, values_b)

        if any(isnan(value) for value in all_values):
            raise ValueError("Wasserstein distance does not accept NaN values.")

        if not all(isfinite(value) for value in chain(values_a, values_b)):
            raise ValueError(
                "Wasserstein distance requires vectors with only finite values."
            )

    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """Compute the 1D Wasserstein distance between two vectors."""
        values_a = [float(value) for value in vector_a.value]
        values_b = [float(value) for value in vector_b.value]
        self._validate_values(values_a, values_b)

        values_a.sort()
        values_b.sort()

        size_a = len(values_a)
        size_b = len(values_b)

        index_a = 0
        index_b = 0
        previous_x = min(values_a[0], values_b[0])
        area = 0.0

        while index_a < size_a or index_b < size_b:
            next_a = values_a[index_a] if index_a < size_a else inf
            next_b = values_b[index_b] if index_b < size_b else inf
            next_x = min(next_a, next_b)

            cdf_a = index_a / size_a
            cdf_b = index_b / size_b
            area += abs(cdf_a - cdf_b) * (next_x - previous_x)

            prior_index_a = index_a
            prior_index_b = index_b

            while index_a < size_a and values_a[index_a] == next_x:
                index_a += 1
            while index_b < size_b and values_b[index_b] == next_x:
                index_b += 1

            if prior_index_a == index_a and prior_index_b == index_b:
                raise ValueError(
                    "Wasserstein distance iteration failed to advance; "
                    "check input values for NaN or unsupported values."
                )

            previous_x = next_x

        return area

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """Compute similarity as the inverse-transformed distance."""
        dist = self.distance(vector_a, vector_b)
        return 1 / (1 + dist)

    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        """Compute Wasserstein distances against multiple vectors."""
        return [self.distance(vector_a, vector_b) for vector_b in vectors_b]

    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        """Compute similarities against multiple vectors."""
        return [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
