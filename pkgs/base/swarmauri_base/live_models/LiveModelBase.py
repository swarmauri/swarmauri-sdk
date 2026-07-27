"""Base behavior shared by live models."""

from abc import abstractmethod
from typing import Literal

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.models.ModelBase import ModelBase
from swarmauri_core.live_models.ILiveConfig import ILiveConfig
from swarmauri_core.live_models.ILiveModel import ILiveModel
from swarmauri_core.live_models.ILiveSession import ILiveSession

from .LiveCapabilitiesBase import LiveCapabilitiesBase
from .LiveSessionBase import LiveSessionBase
from .SyncLiveSessionBase import SyncLiveSessionBase


@ComponentBase.register_model()
class LiveModelBase(ILiveModel, ModelBase):
    capabilities: LiveCapabilitiesBase = Field(
        default_factory=LiveCapabilitiesBase
    )
    resource: str = Field(default=ResourceTypes.LIVE_MODEL.value, frozen=True)
    type: Literal["LiveModelBase"] = "LiveModelBase"

    def connect(self, config: ILiveConfig) -> ILiveSession:
        return SyncLiveSessionBase.create(self.aconnect, config)

    @abstractmethod
    async def aconnect(self, config: ILiveConfig) -> LiveSessionBase: ...
