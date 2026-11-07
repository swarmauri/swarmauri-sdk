from abc import ABC, abstractmethod
from typing import Any


class IMeasurement(ABC):
    """
    Defines a general interface for measurements within the SwarmaURI system.
    Measurements can be anything from system performance measurements to
    machine learning model evaluation measurements.
    """

    @abstractmethod
    def __call__(self, **kwargs: dict[str, Any]) -> Any:
        """
        Retrieves the current value of the measurement.

        Returns:
            The current value of the measurement.
        """
