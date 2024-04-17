from swarmauri.standard.metrics.base.AggregateMetricBase import AggregateMetricBase

class MeanMetric(AggregateMetricBase):
    """
    A metric that calculates the mean (average) of a list of numerical values.

    Attributes:
        name (str): The name of the metric.
        unit (str): The unit of measurement for the mean (e.g., "degrees", "points").
        _value (float): The calculated mean of the measurements.
        _measurements (list): A list of measurements (numerical values) to average.
    """
    def __init__(self, name: str, unit: str):
        """
        Initialize the MeanMetric with its name and unit.

        Args:
            name (str): The name identifier for the metric.
            unit (str): The unit of measurement for the mean.
        """
        # Calling the constructor of the base class
        super().__init__(name, unit)
    
    def add_measurement(self, measurement) -> None:
        """
        Adds a measurement to the internal list of measurements.

        Args:
            measurement (float): A numerical value to be added to the list of measurements.
        """
        # Append the measurement to the internal list
        self._measurements.append(measurement)

    def calculate(self) -> float:
        """
        Calculate the mean of all added measurements.
        
        Returns:
            float: The mean of the measurements or None if no measurements have been added.
        """
        if not self._measurements:
            return None  # Return None if there are no measurements
        # Calculate the mean
        mean = sum(self._measurements) / len(self._measurements)
        # Update the metric's value
        self.update(mean)
        # Return the calculated mean
        return mean