from typing import Any
from abc import ABC, abstractmethod
from swarmauri.core.metrics.IMetric import IMetric
from swarmauri.core.metrics.ICalculateMetric import ICalculateMetric

class CalculateMetricBase(IMetric, ICalculateMetric, ABC):
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
    def value(self):
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
    def calculate(self, **kwargs) -> Any:
        """
        Calculate the metric based on the provided data.
        This method must be implemented by subclasses to define specific calculation logic.
        """
        raise NotImplementedError('calculate is not implemented yet.')

    def update(self, value) -> None:
        """
        Update the metric value based on new information.
        This should be used internally by the `calculate` method or other logic.
        """
        self._value = value

    def __call__(self, **kwargs) -> Any:
        """
        Calculates the metric, updates the value, and returns the current value.
        """
        self.calculate(**kwargs)
        return self.value
