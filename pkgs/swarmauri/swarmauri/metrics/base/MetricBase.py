from typing import Any, Optional, Literal
from pydantic import BaseModel, ConfigDict, Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.metrics.IMetric import IMetric

class MetricBase(IMetric, ComponentBase):
    """
    A base implementation of the IMetric interface that provides the foundation
    for specific metric implementations.
    """
    unit: str
    value: Any = None
    resource: Optional[str] =  Field(default=ResourceTypes.METRIC.value, frozen=True)
    type: Literal['MetricBase'] = 'MetricBase'

    def __call__(self, **kwargs) -> Any:
        """
        Retrieves the current value of the metric.

        Returns:
            The current value of the metric.
        """
        return self.value