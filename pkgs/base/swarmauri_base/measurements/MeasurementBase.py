from typing import Any, Optional, Literal
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.measurements.IMeasurement import IMeasurement


@ComponentBase.register_model()
class MeasurementBase(IMeasurement, ComponentBase):
    """
    A base implementation of the IMeasurement interface that provides the foundation
    for specific measurement implementations.
    """

    unit: str
    value: Any = None
    resource: Optional[str] = Field(
        default=ResourceTypes.MEASUREMENT.value, frozen=True
    )
    type: Literal["MeasurementBase"] = "MeasurementBase"

    def __call__(self, **kwargs) -> Any:
        """
        Retrieves the current value of the measurement.

        Returns:
            The current value of the measurement.
        """
        return self.value
