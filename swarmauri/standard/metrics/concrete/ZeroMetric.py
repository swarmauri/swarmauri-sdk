from swarmauri.standard.metrics.base.MetricBase import MetricBase

class ZeroMetric(MetricBase):
    """
    A concrete implementation of MetricBase that statically represents the value 0.
    This can be used as a placeholder or default metric where dynamic calculation is not required.
    """
    name: str = 'ZeroMetric'
    unit: str = "unitless"
    value: int = 0

    def __call__(self):
        """
        Overrides the value property to always return 0.
        """
        return self.value
