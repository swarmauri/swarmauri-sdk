from swarmauri.standard.metrics.base.AggregateMetricBase import AggregateMetricBase

class FirstImpressionMetric(AggregateMetricBase):
    """
    Metric for capturing the first impression score from a set of scores.
    """

    def __init__(self, name="FirstImpressionScore", unit="points"):
        super().__init__(name=name, unit=unit)
        self._first_impression = None

    def add_measurement(self, measurement) -> None:
        """
        Adds a new score as a measurement. Only the first score is considered as the first impression.
        """
        if self._first_impression is None:
            if isinstance(measurement, (int, float)):
                self._first_impression = measurement
                self._measurements.append(measurement)
            else:
                raise ValueError("Measurement must be a numerical value.")
    
    def calculate(self) -> float:
        """
        Returns the first impression score.

        Returns:
            float: The first impression score.
        """
        if self._first_impression is None:
            raise ValueError("No measurement added. Unable to calculate first impression score.")
        
        self.update(self._first_impression)
        return self.value