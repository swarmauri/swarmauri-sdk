from typing import Any, Literal
from swarmauri.metrics.base.MetricBase import MetricBase

class StaticMetric(MetricBase):
    """
    Metric for capturing the first impression score from a set of scores.
    """
    type: Literal['StaticMetric'] = 'StaticMetric'

    def __call__(self, **kwargs) -> Any:
        """
        Retrieves the current value of the metric.

        Returns:
            The current value of the metric.
        """
        return self.value
