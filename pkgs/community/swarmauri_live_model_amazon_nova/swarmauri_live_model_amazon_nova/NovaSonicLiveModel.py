from typing import Any, Literal, Optional
from pydantic import ConfigDict, Field
from swarmauri_base.live_models.LiveCapabilitiesBase import (
    LiveCapabilitiesBase,
)
from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_base.live_models.LiveModelBase import LiveModelBase
from swarmauri_provider_amazon_nova import AmazonNovaProvider
from .NovaSonicConfigMapper import NovaSonicConfigMapper
from .NovaSonicLiveSession import NovaSonicLiveSession


class NovaSonicLiveModel(LiveModelBase):
    name: str = "amazon.nova-sonic-v1:0"
    provider: AmazonNovaProvider = Field(default_factory=AmazonNovaProvider)
    transport: Optional[Any] = Field(default=None, exclude=True)
    capabilities: LiveCapabilitiesBase = Field(
        default_factory=lambda: LiveCapabilitiesBase(
            input_modalities=frozenset({"text", "audio"}),
            output_modalities=frozenset({"text", "audio"}),
            features=frozenset({"tools"}),
            session_features=frozenset({"realtime", "bidirectional_http2"}),
        )
    )
    type: Literal["NovaSonicLiveModel"] = "NovaSonicLiveModel"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    async def aconnect(self, config: LiveConfigBase):
        if self.transport is None:
            raise ValueError(
                "NovaSonicLiveModel requires an "
                "IBidirectionalStreamClient transport"
            )
        endpoint = (
            f"{self.provider.base_url}/model/{self.name}"
            "/invoke-with-bidirectional-stream"
        )
        connection = await self.transport.aconnect(
            endpoint, **self.provider.connection_options()
        )
        return await NovaSonicLiveSession.create(
            connection, NovaSonicConfigMapper().map(self.name, config)
        )
