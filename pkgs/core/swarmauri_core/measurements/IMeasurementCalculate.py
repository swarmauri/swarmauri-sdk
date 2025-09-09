from typing import Any
from abc import ABC, abstractmethod


class IMeasurementCalculate(ABC):
    @abstractmethod
    def calculate(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
        """
        Calculate the measurement based on the provided data.

        Args:
            *args tuple[Any, ...]: Variable length argument list that the measurement calculation might require.
            **kwargs dict[str, Any]: Arbitrary keyword arguments that the measurement calculation might require.
        """
        pass

    @abstractmethod
    def update(self, value: float) -> None:
        """
        Update the measurement value based on new information.

        Args:
            value float: The new information used to update the measurement. This could be a new measurement or data\
                        point that affects the measurement's current value.

        Note:
            This method is intended for internal use and should not be publicly accessible.
        """
        pass
