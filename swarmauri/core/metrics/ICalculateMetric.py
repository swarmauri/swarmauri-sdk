from typing import Any
from abc import ABC, abstractmethod

class ICalculateMetric(ABC):

    @abstractmethod
    def calculate(self, **kwargs) -> Any:
        """
        Calculate the metric based on the provided data.

        Args:
            *args: Variable length argument list that the metric calculation might require.
            **kwargs: Arbitrary keyword arguments that the metric calculation might require.
        """
        pass

    @abstractmethod
    def update(self, value) -> None:
        """
        Update the metric value based on new information.

        Args:
            value: The new information used to update the metric. This could be a new
            measurement or data point that affects the metric's current value.

        Note:
            This method is intended for internal use and should not be publicly accessible.
        """
        pass

