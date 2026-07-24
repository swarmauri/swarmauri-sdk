"""Base component for lip-sync implementations."""

from abc import abstractmethod
from typing import Any, Literal

from pydantic import ConfigDict, Field, model_validator

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.utils.allowed_models import is_model_allowed
from swarmauri_core.video_lipsync.ILipSync import ILipSync


@ComponentBase.register_model()
class LipSyncBase(ILipSync, ComponentBase):
    """Provide component identity and model-name validation for lip sync."""

    allowed_models: list[str] = []
    resource: str = Field(
        default=ResourceTypes.VIDEO_LIP_SYNC.value, frozen=True
    )
    type: Literal["LipSyncBase"] = "LipSyncBase"
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def _validate_name_in_allowed_models(self) -> "LipSyncBase":
        if self.name and not is_model_allowed(self.name, self.allowed_models):
            raise ValueError(
                f"Model name {self.name} is not allowed. "
                f"Choose from {self.allowed_models}"
            )
        return self

    @abstractmethod
    def predict(
        self,
        video: str,
        audio: str,
        output_path: str = "output.mp4",
        **kwargs: Any,
    ) -> str:
        """Generate lip-synced video and save it locally."""
        raise NotImplementedError

    @abstractmethod
    async def apredict(
        self,
        video: str,
        audio: str,
        output_path: str = "output.mp4",
        **kwargs: Any,
    ) -> str:
        """Asynchronously generate and save lip-synced video."""
        raise NotImplementedError
