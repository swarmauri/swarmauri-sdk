from typing import Literal
from swarmauri_base.measurements.MeasurementBase import MeasurementBase

class ZeroMeasurement(MeasurementBase):
    """
    A concrete implementation of MeasurementBase that statically represents the value 0.
    This can be used as a placeholder or default measurement where dynamic calculation is not required.
    """
    unit: str = "unitless"
    value: int = 0
    type: Literal['ZeroMeasurement'] = 'ZeroMeasurement'

    def __call__(self):
        """
        Overrides the value property to always return 0.
        """
        return self.value
