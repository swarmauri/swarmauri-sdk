from abc import ABC, abstractmethod
from typing import Any, Union, Optional, List, Literal
from pydantic import BaseModel, ConfigDict, ValidationError, model_validator, Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.vcms.IPredictVision import IPredictVision


class VCMBase(IPredictVision, ComponentBase):
    allowed_models: List[str] = []
    resource: Optional[str] = Field(default=ResourceTypes.VCM.value, frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["VCMBase"] = "VCMBase"

    @model_validator(mode="after")
    @classmethod
    def _validate_name_in_allowed_models(cls, values):
        name = values.name
        allowed_models = values.allowed_models
        if name and name not in allowed_models:
            raise ValueError(
                f"Model name {name} is not allowed. Choose from {allowed_models}"
            )
        return values

    def predict(self, *args, **kwargs):
        raise NotImplementedError("Predict not implemented in subclass yet.")
