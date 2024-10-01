from typing import Literal
from swarmauri.metrics.base.MetricBase import MetricBase

class ZeroMetric(MetricBase):
    """
    A concrete implementation of MetricBase that statically represents the value 0.
    This can be used as a placeholder or default metric where dynamic calculation is not required.
    """
    unit: str = "unitless"
    value: int = 0
    type: Literal['ZeroMetric'] = 'ZeroMetric'

    def __call__(self):
        """
        Overrides the value property to always return 0.
        """
        return self.value
