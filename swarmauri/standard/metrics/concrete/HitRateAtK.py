from typing import List, Tuple, Any
from swarmauri.standard.metrics.base.ThresholdMetricBase import ThresholdMetricBase

class HitRateAtK(ThresholdMetricBase):
    """
    Hit Rate at K (HR@K) metric calculates the proportion of times an item of interest 
    appears in the top-K recommendations.
    """

    def __init__(self, name="HitRate@K", unit="ratio", k: int = 5):
        """
        Initializes the Hit Rate at K metric with a specified k value, name, and unit 
        of measurement.
        
        Args:
            k (int): The k value for the top-K recommendations.
            name (str): The name of the metric.
            unit (str): The unit of measurement for the metric.
        """
        super().__init__(name=name, unit=unit, k=k)

    def add_measurement(self, measurement: Tuple[List[Any], Any]) -> None:
        """
        Adds a measurement for HR@K calculation. The measurement should be a tuple
        (recommendations, target), where recommendations is a list of recommended items, 
        and target is the item of interest.

        Args:
            measurement (Tuple[List[Any], Any]): List of recommended items and the target item.
        """
        if len(measurement) != 2 or not isinstance(measurement[0], list):
            raise ValueError("Measurement must be a tuple (recommendations, target).")
        self._measurements.append(measurement)

    def calculate(self) -> Any:
        """
        Calculate the HR@K based on the provided measurements.

        Returns:
            Any: The HR@K score as a floating point number.
        """
        if not self._measurements:
            raise ValueError("No measurements added to calculate HR@K.")

        hits = 0
        for recommendations, target in self._measurements:
            hits += 1 if target in recommendations[:self.k] else 0

        hit_rate_at_k = hits / len(self._measurements)

        self.update(hit_rate_at_k)
        return self.value

    def reset(self) -> None:
        """
        Resets the metric's state/value, allowing for fresh calculations.
        """
        super().reset()