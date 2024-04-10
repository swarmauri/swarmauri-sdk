from typing import Any
from abc import ABC, abstractmethod
from swarmauri.core.metrics.IMetric import IMetric

class MetricBase(IMetric, ABC):
    """
    A base implementation of the IMetric interface that provides the foundation
    for specific metric implementations.
    """

    def __init__(self, name: str, unit: str):
        """
        Initializes the metric with a name and unit of measurement.

        Args:
            name (str): The name of the metric.
            unit (str): The unit of measurement for the metric (e.g., 'seconds', 'accuracy').
        """
        self._name = name
        self._unit = unit
        self._value = None  # Initialize with None, or a default value as appropriate

    @property
    def name(self) -> str:
        """
        The metric's name identifier.
        """
        return self._name

    @property
    def value(self) -> Any:
        """
        The current value of the metric.
        """
        return self._value

    @property
    def unit(self) -> str:
        """
        The unit of measurement for the metric.
        """
        return self._unit

    @unit.setter
    def unit(self, value: str) -> None:
        """
        Set the unit of measurement for the metric.
        """
        self._unit = value

    @abstractmethod
    def __call__(self, **kwargs) -> Any:
        """
        Retrieves the current value of the metric.

        Returns:
            The current value of the metric.
        """
        return self.value