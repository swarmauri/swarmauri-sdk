from abc import abstractmethod
from typing import List, Literal, Optional

from pydantic import ConfigDict, Field, model_validator
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.vlms.IPredictVision import IPredictVision


@ComponentBase.register_model()
class VLMBase(IPredictVision, ComponentBase):
    allowed_models: List[str] = []
    resource: Optional[str] = Field(default=ResourceTypes.VLM.value, frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["VLMBase"] = "VLMBase"

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

    def add_allowed_model(self, model: str) -> None:
        """
        Add a new model to the list of allowed models.

        Raises:
            ValueError: If the model is already in the allowed models list.
        """
        if model in self.allowed_models:
            raise ValueError(f"Model '{model}' is already allowed.")
        self.allowed_models.append(model)

    def remove_allowed_model(self, model: str) -> None:
        """
        Remove a model from the list of allowed models.

        Raises:
            ValueError: If the model is not in the allowed models list.
        """
        if model not in self.allowed_models:
            raise ValueError(f"Model '{model}' is not in the allowed models list.")
        self.allowed_models.remove(model)

    @abstractmethod
    def predict_vision(self, *args, **kwargs):
        raise NotImplementedError("predict_vision() not implemented in subclass yet.")

    @abstractmethod
    async def apredict_vision(self, *args, **kwargs):
        raise NotImplementedError("apredict_vision() not implemented in subclass yet.")

    @abstractmethod
    def batch(self, *args, **kwargs):
        raise NotImplementedError("batch() not implemented in subclass yet.")

    @abstractmethod
    async def abatch(self, *args, **kwargs):
        raise NotImplementedError("abatch() not implemented in subclass yet.")
