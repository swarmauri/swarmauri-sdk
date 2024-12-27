from typing import Any, Literal
from swarmauri_base.measurements.MeasurementBase import MeasurementBase

class FirstImpressionMeasurement(MeasurementBase):
    """
    Measurement for capturing the first impression score from a set of scores.
    """
    type: Literal['FirstImpressionMeasurement'] = 'FirstImpressionMeasurement'
    def __call__(self, **kwargs) -> Any:
        """
        Retrieves the current value of the measurement.

        Returns:
            The current value of the measurement.
        """
        return self.value
