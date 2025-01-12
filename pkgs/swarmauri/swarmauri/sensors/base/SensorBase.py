# swarmauri/sensors/base/SensorBase.py
from typing import Literal, Optional

from pydantic import ConfigDict, Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.sensors.ISensor import ISensor


class SensorBase(ISensor, ComponentBase):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    resource: Optional[str] = Field(default=ResourceTypes.SENSOR.value, frozen=True)
    type: Literal["SensorBase"] = "SensorBase"

    def read(self) -> any:
        raise NotImplementedError("Subclass must implement the read method")
