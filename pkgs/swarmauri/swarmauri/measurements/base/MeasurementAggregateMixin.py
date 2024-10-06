from typing import List, Any, Literal
from pydantic import BaseModel
from swarmauri_core.measurements.IMeasurementAggregate import IMeasurementAggregate

class MeasurementAggregateMixin(IMeasurementAggregate, BaseModel):
    """
    An abstract base class that implements the IMeasurement interface, providing common 
    functionalities and properties for measurements within SwarmAURI.
    """
    measurements: List[Any] = []

    
    def add_measurement(self, measurement) -> None:
        """
        Adds measurement to the internal store of measurements.
        """
        self.measurements.append(measurement)

    def reset(self) -> None:
        """
        Resets the measurement's state/value, allowing for fresh calculations.
        """
        self.measurements.clear()
        self.value = None

