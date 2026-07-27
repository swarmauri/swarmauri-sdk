from typing import Any, Literal
from pydantic import ConfigDict, Field
from swarmauri_base.live_models import (
    LiveCapabilitiesBase,
    LiveConfigBase,
    LiveModelBase,
)
from swarmauri_provider_xai import XAIProvider
from swarmauri_transport_websocket import WebSocketClient
from .XAIRealtimeConfigMapper import XAIRealtimeConfigMapper
from .XAIRealtimeSession import XAIRealtimeSession


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
        api_key = self.provider.connection_options().get("api_key")
        if not api_key:
            raise ValueError("XAIProvider requires an api_key")
        connection = await self.transport.aconnect(
            self.provider.endpoints.websocket_url,
            headers={"Authorization": f"Bearer {api_key}"},
        )
        return await XAIRealtimeSession.create(
            connection, XAIRealtimeConfigMapper().map(config)
        )
