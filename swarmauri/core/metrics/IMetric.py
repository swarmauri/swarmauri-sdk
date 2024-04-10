from abc import ABC, abstractmethod

class IMetric(ABC):
    """
    Defines a general interface for metrics within the SwarmaURI system.
    Metrics can be anything from system performance measurements to
    machine learning model evaluation metrics.
    """

    @property
    def name(self) -> str:
        """
        The name identifier for the metric.

        Returns:
            str: The name of the metric.
        """
        pass

    @property
    def value(self):
        """
        Current value of the metric.

        Returns:
            The metric's value. The type depends on the specific metric implementation.
        """
        pass  

    @abstractmethod
    def calculate(self, data) -> None:
        """
        Calculate the metric based on the provided data.

        Args:
            data: The data needed to calculate the metric. The type and form of this data
            would depend on the nature of the metric being calculated.
        """
        pass

    @abstractmethod
    def update(self, value) -> None:
        """
        Update the metric value based on new information.

        Args:
            value: The new information used to update the metric. This could be a new
            measurement or data point that affects the metric's current value.
        """
        pass

    @abstractmethod
    def get_value(self):
        """
        Retrieve the current value of the metric.

        Returns:
            The current metric value. The type of this value can vary depending on the metric.
        """
        pass

