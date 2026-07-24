from abc import abstractmethod
from collections.abc import AsyncIterator, Iterator, Mapping
from typing import Any, List, Literal, Optional

from pydantic import ConfigDict, model_validator, Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.utils.allowed_models import is_model_allowed
from swarmauri_core.tts.ITextToSpeech import ITextToSpeech


@ComponentBase.register_model()
class TTSBase(ITextToSpeech, ComponentBase):
    allowed_models: List[str] = []
    resource: Optional[str] = Field(
        default=ResourceTypes.TTS.value, frozen=True
    )
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["TTSBase"] = "TTSBase"

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
    def predict(self, text: str, audio_path: str = "output.mp3") -> str:
        raise NotImplementedError("predict() not implemented in subclass yet.")

    @abstractmethod
    async def apredict(self, text: str, audio_path: str = "output.mp3") -> str:
        raise NotImplementedError(
            "apredict() not implemented in subclass yet."
        )

    @abstractmethod
    def stream(self, text: str, **kwargs: Any) -> Iterator[bytes]:
        raise NotImplementedError("stream() not implemented in subclass yet.")

    @abstractmethod
    async def astream(self, text: str, **kwargs: Any) -> AsyncIterator[bytes]:
        raise NotImplementedError("astream() not implemented in subclass yet.")

    @abstractmethod
    def batch(self, text_path_dict: Mapping[str, str]) -> list[str]:
        raise NotImplementedError("batch() not implemented in subclass yet.")

    @abstractmethod
    async def abatch(
        self,
        text_path_dict: Mapping[str, str],
        max_concurrent: int = 5,
    ) -> list[str]:
        raise NotImplementedError("abatch() not implemented in subclass yet.")
