from abc import ABC, abstractmethod
from swarmauri.standard.metrics.base.MetricBase import MetricBase
from swarmauri.core.metrics.IResetMetric import IResetMetric

class ResetableMetricBase(MetricBase, IResetMetric, ABC):
    """
    An abstract base class that implements the IMetric interface, providing common 
    functionalities and properties for metrics within SwarmAURI.
    """
    def __init__(self, name: str):
        MetricBase.__init__(name)

    def reset(self) -> None:
        """
        Resets the metric's state/value, allowing for fresh calculations.
        """
        self._value = None

