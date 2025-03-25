from abc import abstractmethod
from typing import Dict, List, Literal, Optional

from pydantic import ConfigDict, Field, PrivateAttr, SecretStr, model_validator
from swarmauri_core.llms.IPredict import IPredict

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class LLMBase(IPredict, ComponentBase):
    allowed_models: List[str] = []
    resource: Optional[str] = Field(default=ResourceTypes.LLM.value, frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["LLMBase"] = "LLMBase"

    # Common attributes found in both GroqModel and OpenAIModel
    api_key: Optional[SecretStr] = None
    name: str = ""
    timeout: float = 600.0
    include_usage: bool = True

    # Base URL to be overridden by subclasses
    BASE_URL: Optional[str] = None
    _headers: Dict[str, str] = PrivateAttr(default=None)

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
    def _format_messages(self, *args, **kwargs):
        """Format conversation messages for API request."""
        raise NotImplementedError("_format_messages() not implemented in subclass yet.")

    @abstractmethod
    def get_allowed_models(self) -> List[str]:
        """Get the list of allowed models for this LLM provider."""
        raise NotImplementedError(
            "get_allowed_models() not implemented in subclass yet."
        )

    @abstractmethod
    def predict(self, *args, **kwargs):
        raise NotImplementedError("predict() not implemented in subclass yet.")

    @abstractmethod
    async def apredict(self, *args, **kwargs):
        raise NotImplementedError("apredict() not implemented in subclass yet.")

    @abstractmethod
    def stream(self, *args, **kwargs):
        raise NotImplementedError("stream() not implemented in subclass yet.")

    @abstractmethod
    async def astream(self, *args, **kwargs):
        raise NotImplementedError("astream() not implemented in subclass yet.")

    @abstractmethod
    def batch(self, *args, **kwargs):
        raise NotImplementedError("batch() not implemented in subclass yet.")

    @abstractmethod
    async def abatch(self, *args, **kwargs):
        raise NotImplementedError("abatch() not implemented in subclass yet.")
