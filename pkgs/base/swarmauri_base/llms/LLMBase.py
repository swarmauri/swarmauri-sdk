from abc import abstractmethod
from typing import ClassVar, Dict, FrozenSet, List, Literal, Optional

from pydantic import Field, PrivateAttr, SecretStr, model_validator
from swarmauri_core.llms.IPredict import IPredict

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.utils.allowed_models import is_model_allowed


@ComponentBase.register_model()
class LLMBase(IPredict, ComponentBase):
    allowed_models: List[str] = Field(default_factory=list)
    resource: Optional[str] = Field(
        default=ResourceTypes.LLM.value, frozen=True
    )
    type: Literal["LLMBase"] = "LLMBase"

    api_key: Optional[SecretStr] = Field(default=None, exclude=True)
    name: str = ""
    timeout: float = 600.0
    include_usage: bool = True
    max_retries: int = Field(default=3, ge=1)
    retry_delay: float = Field(default=2.0, ge=0)

    capabilities: ClassVar[FrozenSet[str]] = frozenset()
    retryable_status_codes: ClassVar[FrozenSet[int]] = frozenset(
        {408, 409, 425, 429, 500, 502, 503, 504, 529}
    )

    # Base URL to be overridden by subclasses
    BASE_URL: Optional[str] = None
    _headers: Dict[str, str] = PrivateAttr(default_factory=dict)

    @model_validator(mode="after")
    def _validate_name_in_allowed_models(self):
        name = self.name
        allowed_models = self.allowed_models
        if name and not is_model_allowed(name, allowed_models):
            raise ValueError(
                (
                    f"Model name {name} is not allowed. Choose from "
                    f"{allowed_models}"
                )
            )
        return self

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
            raise ValueError(
                f"Model '{model}' is not in the allowed models list."
            )
        self.allowed_models.remove(model)

    @abstractmethod
    def predict(self, *args, **kwargs):
        raise NotImplementedError("predict() not implemented in subclass yet.")

    @abstractmethod
    async def apredict(self, *args, **kwargs):
        raise NotImplementedError(
            "apredict() not implemented in subclass yet."
        )

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
