from typing import List, Any
from abc import ABC, abstractmethod
from swarmauri.standard.metrics.base.CalculateMetricBase import CalculateMetricBase
from swarmauri.core.metrics.IAggMeasurements import IAggMeasurements

class AggregateMetricBase(CalculateMetricBase, IAggMeasurements, ABC):
    """
    An abstract base class that implements the IMetric interface, providing common 
    functionalities and properties for metrics within SwarmAURI.
    """
    def __init__(self, name: str, unit: str):
        CalculateMetricBase.__init__(name, unit)
        self._measurements = []

    @abstractmethod
    def add_measurement(self, measurement) -> None:
        """
        Adds measurement to the internal store of measurements.
        """
        self._measurements.append(measurement)

    @property
    def measurements(self) -> List[Any]:
        return self._measurements

    @measurements.setter
    def measurements(self, value) -> None:
        self._measurements = value

    def reset(self) -> None:
        """
        Resets the metric's state/value, allowing for fresh calculations.
        """
        self._measurements.clear()
        self._value = None

