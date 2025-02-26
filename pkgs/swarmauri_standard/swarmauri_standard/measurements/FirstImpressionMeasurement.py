import warnings

from typing import Any, Literal
from swarmauri_base.measurements.MeasurementBase import MeasurementBase
from swarmauri_base.ComponentBase import ComponentBase


warnings.warn(
    "Importing ComponentBase from swarmauri_core is deprecated and will be "
    "removed in a future version. Please use 'from swarmauri_base import "
    "ComponentBase'",
    DeprecationWarning,
    stacklevel=2,
)



@ComponentBase.register_type(MeasurementBase, "FirstImpressionMeasurement")
class FirstImpressionMeasurement(MeasurementBase):
    """
    Measurement for capturing the first impression score from a set of scores.
    """

    type: Literal["FirstImpressionMeasurement"] = "FirstImpressionMeasurement"

    def __call__(self, **kwargs) -> Any:
        """
        Retrieves the current value of the measurement.

        Returns:
            The current value of the measurement.
        """
        return self.value
