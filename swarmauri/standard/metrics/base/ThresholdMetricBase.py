from abc import ABC, abstractmethod
from swarmauri.standard.metrics.base.AggregateMetricBase import AggregateMetricBase
from swarmauri.core.metrics.IAggMeasurements import IAggMeasurements
from swarmauri.core.metrics.IThreshold import IThreshold

class ThresholdMetricBase(AggregateMetricBase, IAggMeasurements, ABC):
    """
    An abstract base class that implements the IMetric interface, providing common 
    functionalities and properties for metrics within SwarmAURI.
    """
    def __init__(self, name: str, unit: str, k: int):
        AggregateMetricBase.__init__(name, unit)
        self._k = k

    @property
    @abstractmethod
    def k(self) -> int:
        return self._k

    @k.setter
    @abstractmethod
    def k(self, value: int) -> None:
        self._k = value
