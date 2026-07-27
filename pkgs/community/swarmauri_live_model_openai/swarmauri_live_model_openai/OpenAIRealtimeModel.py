from typing import Any, Literal
from urllib.parse import urlencode
from pydantic import ConfigDict, Field
from swarmauri_base.live_models.LiveCapabilitiesBase import (
    LiveCapabilitiesBase,
)
from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_base.live_models.LiveModelBase import LiveModelBase
from swarmauri_provider_openai import OpenAIProvider
from swarmauri_transport_websocket import WebSocketClient
from .OpenAIRealtimeConfigMapper import OpenAIRealtimeConfigMapper
from .OpenAIRealtimeSession import OpenAIRealtimeSession


class OpenAIRealtimeModel(LiveModelBase):
    name: str = "gpt-realtime"
    provider: OpenAIProvider = Field(default_factory=OpenAIProvider)
    transport: Any = Field(default_factory=WebSocketClient, exclude=True)
    capabilities: LiveCapabilitiesBase = Field(
        default_factory=lambda: LiveCapabilitiesBase(
            input_modalities=frozenset({"text", "audio", "image"}),
            output_modalities=frozenset({"text", "audio"}),
            features=frozenset({"tools", "transcription"}),
            session_features=frozenset({"realtime", "interruption"}),
        )
    )
    type: Literal["OpenAIRealtimeModel"] = "OpenAIRealtimeModel"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    async def aconnect(self, config: LiveConfigBase) -> OpenAIRealtimeSession:
        api_key = self.provider.connection_options().get("api_key")
        if not api_key:
            raise ValueError("OpenAIProvider requires an api_key")
        query = urlencode({"model": self.name})
        url = f"{self.provider.endpoints.realtime_url}?{query}"
        connection = await self.transport.aconnect(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "OpenAI-Beta": "realtime=v1",
            },
        )
        return await OpenAIRealtimeSession.create(
            connection, OpenAIRealtimeConfigMapper().map(config)
        )
