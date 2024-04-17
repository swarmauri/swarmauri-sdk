from swarmauri.standard.metrics.base.AggregateMetricBase import AggregateMetricBase

class SystemUsabilityScaleMetric(AggregateMetricBase):
    """
    Metric calculating the System Usability Scale (SUS) score based on a set of questionnaire responses.
    """
    
    def __init__(self):
        super().__init__(name="SystemUsabilityScale", unit="SUS score")

    def add_measurement(self, measurement) -> None:
        """
        Adds individual SUS questionnaire item scores (ranging from 0-4) to the measurements.
        """
        if isinstance(measurement, list) and all(isinstance(item, int) and 0 <= item <= 4 for item in measurement):
            self._measurements.extend(measurement)
        else:
            raise ValueError("Each measurement must be a list of integers between 0 and 4.")

    def calculate(self, **kwargs) -> float:
        """
        Calculate the SUS score from the current measurements.
        
        Returns:
            float: The calculated SUS score.
        """
        if len(self._measurements) != 10:
            raise ValueError("Exactly 10 measurements are required to calculate the SUS score.")
        
        # Adjust scores for negative items: subtract each score from 4
        adjusted_scores = [self._measurements[i] if i % 2 == 0 else 4 - self._measurements[i] for i in range(10)]
        
        # Calculate the SUS score: multiply the sum of scores by 2.5
        sus_score = sum(adjusted_scores) * 2.5
        self.update(sus_score)
        return self.value