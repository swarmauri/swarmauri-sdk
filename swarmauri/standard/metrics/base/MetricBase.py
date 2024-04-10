from abc import ABC, abstractmethod
from swarmauri.core.metrics.IMetric import IMetric

class MetricBase(IMetric, ABC):
    """
    An abstract base class that implements the IMetric interface, providing common 
    functionalities and properties for metrics within SwarmaURI.
    """

    def __init__(self, name: str):
        """
        Initializes the MetricBase with a specific name identifying the metric.

        Args:
            name (str): The name of the metric.
        """
        self._name = name
        self._value = None

    @property
    def name(self) -> str:
        """
        The name identifier for the metric.

        Returns:
            str: The name of the metric.
        """
        return self._name

    @property
    def value(self):
        """
        Current value of the metric.

        Returns:
            The metric's value. The type depends on the specific metric implementation.
        """
        return self._value

    @abstractmethod
    def calculate(self, data) -> None:
        """
        Abstract method to calculate the metric based on provided data. This needs to 
        be implemented by subclasses.

        Args:
            data: Input data needed for calculating the metric.
        """
        raise NotImplementedError('calculate not implemented')

    def update(self, value) -> None:
        """
        Updates the metric's current value.

        Args:
            value: New value or information to update the metric with.
        """
        self._value = value

    def get_value(self):
        """
        Retrieves the current value of the metric.

        Returns:
            The current value of the metric.
        """
        return self.value

    def __call__(self, data):
        """
        Retrieves the current value of the metric.

        Returns:
            The current value of the metric.
        """
        self.update(self.calculate(data))
        return self.value
