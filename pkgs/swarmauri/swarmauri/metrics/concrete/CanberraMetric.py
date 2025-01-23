from swarmauri.metrics.metricbase import MetricBase
from swarmauri.vectors.concrete.Vector import Vector
from typing import Literal
import numpy as np


class CanberraMetric(MetricBase):
    """
    Concrete implementation of the Canberra distance metric.
    """
    type: Literal['CanberraMetric'] = 'CanberraMetric'

    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Canberra distance between two vectors.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.

        Returns:
            float: The computed Canberra distance.
        """
        data_a = np.array(vector_a.value)
        data_b = np.array(vector_b.value)

        if data_a.shape != data_b.shape:
            raise ValueError("Vectors must have the same dimensionality.")

        differences = np.abs(data_a - data_b)
        sums = np.abs(data_a) + np.abs(data_b)

        # Avoid division by zero by excluding zero terms from the computation
        non_zero_indices = sums != 0
        canberra_distance = np.sum(differences[non_zero_indices] / sums[non_zero_indices])

        return canberra_distance

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes similarity based on the Canberra distance using exponential decay.

        Args:
            vector_a (Vector): The first vector.
            vector_b (Vector): The second vector.

        Returns:
            float: A similarity score between 0 and 1.
        """
        dist = self.distance(vector_a, vector_b)
        return np.exp(-dist)  # Exponential decay similarity
