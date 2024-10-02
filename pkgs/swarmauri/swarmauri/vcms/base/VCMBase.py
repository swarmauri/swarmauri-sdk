from abc import ABC, abstractmethod
from typing import Any, Union, Optional, List, Literal
from pydantic import BaseModel, ConfigDict, ValidationError, model_validator, Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.vcms.IPredictVision import IPredictVision


class VCMBase(IPredictVision, ComponentBase):
    # allowed_models: List[str] = []
    resource: Optional[str] = Field(default=ResourceTypes.VCM.value, frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["VCMBase"] = "VCMBase"


    def predict_vision(self, *args, **kwargs):
        raise NotImplementedError("Predict not implemented in subclass yet.")
