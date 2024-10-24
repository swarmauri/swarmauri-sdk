from typing import Any
from abc import ABC, abstractmethod

class IMeasurementCalculate(ABC):

    @abstractmethod
    def calculate(self, **kwargs) -> Any:
        """
        Calculate the measurement based on the provided data.

        Args:
            *args: Variable length argument list that the measurement calculation might require.
            **kwargs: Arbitrary keyword arguments that the measurement calculation might require.
        """
        pass

    @abstractmethod
    def update(self, value) -> None:
        """
        Update the measurement value based on new information.

        Args:
            value: The new information used to update the measurement. This could be a new
            measurement or data point that affects the measurement's current value.

        Note:
            This method is intended for internal use and should not be publicly accessible.
        """
        pass
        