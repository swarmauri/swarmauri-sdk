from typing import List, Any, Literal
from pydantic import BaseModel
from swarmauri_core.metrics.IMetricAggregate import IMetricAggregate

class MetricAggregateMixin(IMetricAggregate, BaseModel):
    """
    An abstract base class that implements the IMetric interface, providing common 
    functionalities and properties for metrics within SwarmAURI.
    """
    measurements: List[Any] = []

    
    def add_measurement(self, measurement) -> None:
        """
        Adds measurement to the internal store of measurements.
        """
        self.measurements.append(measurement)

    def reset(self) -> None:
        """
        Resets the metric's state/value, allowing for fresh calculations.
        """
        self.measurements.clear()
        self.value = None

