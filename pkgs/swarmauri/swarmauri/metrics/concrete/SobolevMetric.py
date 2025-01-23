from typing import Literal
import numpy as np

from swarmauri.metrics.metricbase import MetricBase
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.norms.concrete.SobolevNorm import SobolevNorm


class SobolevMetric(MetricBase):
    """
    Concrete implementation of the Sobolev distance metric.
    Uses the SobolevNorm to compute the distance between two vectors.
    """
    type: Literal['SobolevMetric'] = 'SobolevMetric'
    norm: SobolevNorm = SobolevNorm()

    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Sobolev distance between two vectors using the Sobolev norm.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.

        Returns:
            float: The computed Sobolev distance.
        """
        # Use the SobolevNorm to compute the norm (distance)
        distance = self.norm.compute(vector_a - vector_b)
        return distance

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes similarity based on the Sobolev distance using exponential decay.

        Args:
            vector_a (Vector): The first vector.
            vector_b (Vector): The second vector.

        Returns:
            float: A similarity score between 0 and 1.
        """
        dist = self.distance(vector_a, vector_b)
        return np.exp(-dist)  # Exponential decay similarity
