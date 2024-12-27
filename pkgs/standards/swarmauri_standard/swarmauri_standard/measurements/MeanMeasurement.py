from typing import Literal
from swarmauri_base.measurements.MeasurementBase import MeasurementBase
from swarmauri_base.measurements.MeasurementCalculateMixin import MeasurementCalculateMixin
from swarmauri_base.measurements.MeasurementAggregateMixin import MeasurementAggregateMixin

class MeanMeasurement(MeasurementAggregateMixin, MeasurementCalculateMixin, MeasurementBase):
    """
    A measurement that calculates the mean (average) of a list of numerical values.

    Attributes:
        name (str): The name of the measurement.
        unit (str): The unit of measurement for the mean (e.g., "degrees", "points").
        _value (float): The calculated mean of the measurements.
        _measurements (list): A list of measurements (numerical values) to average.
    """
    type: Literal['MeanMeasurement'] = 'MeanMeasurement'

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
        # Update the measurement's value
        self.update(mean)
        # Return the calculated mean
        return mean