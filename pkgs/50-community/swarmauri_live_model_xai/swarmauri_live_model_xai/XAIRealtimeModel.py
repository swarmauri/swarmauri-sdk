from typing import Any, Literal

from pydantic import ConfigDict, Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.live_models.LiveCapabilitiesBase import (
    LiveCapabilitiesBase,
)
from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_base.live_models.LiveModelBase import LiveModelBase
from swarmauri_provider_xai import XAIProvider
from swarmauri_transport_websocket import WebSocketClient

from .XAIRealtimeConfigMapper import XAIRealtimeConfigMapper
from .XAIRealtimeSession import XAIRealtimeSession


@ComponentBase.register_type(LiveModelBase, "XAIRealtimeModel")
class XAIRealtimeModel(LiveModelBase):
    name: str = "grok-realtime"
    provider: XAIProvider = Field(default_factory=XAIProvider)
    transport: Any = Field(default_factory=WebSocketClient, exclude=True)
    capabilities: LiveCapabilitiesBase = Field(
        default_factory=lambda: LiveCapabilitiesBase(
            input_modalities=frozenset({"text", "audio"}),
            output_modalities=frozenset({"text", "audio"}),
            features=frozenset({"tools"}),
            session_features=frozenset({"realtime"}),
        )
    )
    type: Literal["XAIRealtimeModel"] = "XAIRealtimeModel"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    async def aconnect(self, config: LiveConfigBase):
        connection_config = self.provider.prepare_connection(
            "realtime.connect", model=self.name
        )
        connection = await self.transport.aconnect(
            connection_config.resolved_url(),
            headers=connection_config.headers,
        )
        return await XAIRealtimeSession.create(
            connection, XAIRealtimeConfigMapper().map(config)
        )
