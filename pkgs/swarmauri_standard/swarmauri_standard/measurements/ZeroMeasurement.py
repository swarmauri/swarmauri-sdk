import warnings

from typing import Literal
from swarmauri_base.measurements.MeasurementBase import MeasurementBase
from swarmauri_base.ComponentBase import ComponentBase


warnings.warn(
    "Importing ComponentBase from swarmauri_core is deprecated and will be "
    "removed in a future version. Please use 'from swarmauri_base import "
    "ComponentBase'",
    DeprecationWarning,
    stacklevel=2,
)



@ComponentBase.register_type(MeasurementBase, "ZeroMeasurement")
class ZeroMeasurement(MeasurementBase):
    """
    A concrete implementation of MeasurementBase that statically represents the value 0.
    This can be used as a placeholder or default measurement where dynamic calculation is not required.
    """

    unit: str = "unitless"
    value: int = 0
    type: Literal["ZeroMeasurement"] = "ZeroMeasurement"

    def __call__(self):
        """
        Overrides the value property to always return 0.
        """
        return self.value
