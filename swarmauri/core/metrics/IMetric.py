from typing import Any
from abc import ABC, abstractmethod

class IMetric(ABC):
    """
    Defines a general interface for metrics within the SwarmaURI system.
    Metrics can be anything from system performance measurements to
    machine learning model evaluation metrics.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name identifier for the metric.

        Returns:
            str: The name of the metric.
        """
        pass

    @property
    @abstractmethod
    def value(self) -> Any:
        """
        Current value of the metric.

        Returns:
            The metric's value. The type depends on the specific metric implementation.
        """
        pass

    @property
    @abstractmethod
    def unit(self) -> str:
        """
        The unit of measurement for the metric.

        Returns:
            str: The unit of measurement (e.g., 'seconds', 'Mbps').
        """
        pass

    @unit.setter
    @abstractmethod
    def unit(self, value: str) -> None:
        """
        Update the unit of measurement for the metric.

        Args:
            value (str): The new unit of measurement for the metric.
        """
        pass

    @abstractmethod
    def __call__(self, **kwargs) -> Any:
        """
        Retrieves the current value of the metric.

        Returns:
            The current value of the metric.
        """
        pass