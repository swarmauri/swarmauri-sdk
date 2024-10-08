from abc import ABC, abstractmethod
from typing import Any, Union, Optional, List, Literal
from pydantic import BaseModel, ConfigDict, ValidationError, model_validator, Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.llms.IPredict import IPredict


class LLMBase(IPredict, ComponentBase):
    allowed_models: List[str] = []
    resource: Optional[str] = Field(default=ResourceTypes.LLM.value, frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["LLMBase"] = "LLMBase"

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
        raise NotImplementedError("predict() not implemented in subclass yet.")

    async def apredict(self, *args, **kwargs):
        raise NotImplementedError("apredict() not implemented in subclass yet.")

    def stream(self, *args, **kwargs):
        raise NotImplementedError("stream() not implemented in subclass yet.")

    async def astream(self, *args, **kwargs):
        raise NotImplementedError("astream() not implemented in subclass yet.")

    def batch(self, *args, **kwargs):
        raise NotImplementedError("batch() not implemented in subclass yet.")

    async def abatch(self, *args, **kwargs):
        raise NotImplementedError("abatch() not implemented in subclass yet.")