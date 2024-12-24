from abc import abstractmethod
from typing import Any, Literal
from pydantic import BaseModel
from swarmauri_core.measurements.IMeasurementCalculate import IMeasurementCalculate

class MeasurementCalculateMixin(IMeasurementCalculate, BaseModel):
    """
    A base implementation of the IMeasurement interface that provides the foundation
    for specific measurement implementations.
    """
    
    def update(self, value) -> None:
        """
        Update the measurement value based on new information.
        This should be used internally by the `calculate` method or other logic.
        """
        self.value = value

    @abstractmethod
    def calculate(self, **kwargs) -> Any:
        """
        Calculate the measurement based on the provided data.
        This method must be implemented by subclasses to define specific calculation logic.
        """
        raise NotImplementedError('calculate is not implemented yet.')
    
    def __call__(self, **kwargs) -> Any:
        """
        Calculates the measurement, updates the value, and returns the current value.
        """
        self.calculate(**kwargs)
        return self.value
