from typing import Optional, Literal
from pydantic import ConfigDict, Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.vcms.IPredictVision import IPredictVision

class VCMBase(IPredictVision, ComponentBase):
    resource: Optional[str] = Field(default=ResourceTypes.VCM.value, frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["VCMBase"] = "VCMBase"

    def predict_vision(self, *args, **kwargs):
        raise NotImplementedError("Predict not implemented in subclass yet.")
