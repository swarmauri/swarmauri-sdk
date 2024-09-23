from typing import Literal
from swarmauri.metrics.base.MetricBase import MetricBase
from swarmauri.metrics.base.MetricCalculateMixin import MetricCalculateMixin
from swarmauri.metrics.base.MetricAggregateMixin import MetricAggregateMixin

class MeanMetric(MetricAggregateMixin, MetricCalculateMixin, MetricBase):
    """
    A metric that calculates the mean (average) of a list of numerical values.

    Attributes:
        name (str): The name of the metric.
        unit (str): The unit of measurement for the mean (e.g., "degrees", "points").
        _value (float): The calculated mean of the measurements.
        _measurements (list): A list of measurements (numerical values) to average.
    """
    type: Literal['MeanMetric'] = 'MeanMetric'

    def add_measurement(self, measurement: int) -> None:
        """
        Adds a measurement to the internal list of measurements.

        Args:
            measurement (float): A numerical value to be added to the list of measurements.
        """
        # Append the measurement to the internal list
        self.measurements.append(measurement)

    def calculate(self) -> float:
        """
        Calculate the mean of all added measurements.
        
        Returns:
            float: The mean of the measurements or None if no measurements have been added.
        """
        if not self.measurements:
            return None  # Return None if there are no measurements
        # Calculate the mean
        mean = sum(self.measurements) / len(self.measurements)
        # Update the metric's value
        self.update(mean)
        # Return the calculated mean
        return mean