from swarmauri.standard.metrics.base.ThresholdMetricBase import ThresholdMetricBase

class ThresholdMeanMetric(ThresholdMetricBase):
    """
    Calculates the mean of measurements that fall within a specified threshold from the current mean.
    """

    def is_within_threshold(self, measurement: float) -> bool:
        if self._value is None:  # If there's no current value, accept the measurement
            return True
        return abs(measurement - self._value) <= self.threshold
    
    def calculate(self) -> float:
        # Filtering the measurements based on the threshold
        filtered_measurements = [m for m in self._measurements if self.is_within_threshold(m)]

        # Calculate the mean of filtered measurements
        if not filtered_measurements:
            return None  # Return None if there are no measurements within the threshold

        mean_value = sum(filtered_measurements) / len(filtered_measurements)
        self.update(mean_value)
        return mean_value