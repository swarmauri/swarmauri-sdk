from typing import Any, Literal
from urllib.parse import quote

from pydantic import ConfigDict, Field

from swarmauri_base.live_models.LiveCapabilitiesBase import (
    LiveCapabilitiesBase,
)
from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_base.live_models.LiveModelBase import LiveModelBase
from swarmauri_provider_gemini import GeminiProvider
from swarmauri_transport_websocket import WebSocketClient

from .GeminiLiveConfigMapper import GeminiLiveConfigMapper
from .GeminiLiveSession import GeminiLiveSession


class GeminiLiveModel(LiveModelBase):
    name: str = "gemini-3.1-flash-live-preview"
    provider: GeminiProvider = Field(default_factory=GeminiProvider)
    transport: Any = Field(default_factory=WebSocketClient, exclude=True)
    capabilities: LiveCapabilitiesBase = Field(
        default_factory=lambda: LiveCapabilitiesBase(
            input_modalities=frozenset({"text", "audio", "image", "video"}),
            output_modalities=frozenset({"text", "audio"}),
            features=frozenset({"tools", "transcription"}),
            session_features=frozenset(
                {"realtime", "interruption", "session_resumption"}
            ),
        )
    )
    type: Literal["GeminiLiveModel"] = "GeminiLiveModel"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    async def aconnect(self, config: LiveConfigBase) -> GeminiLiveSession:
        api_key = self.provider.connection_options().get("api_key")
        if not api_key:
            raise ValueError("GeminiProvider requires an api_key")
        url = f"{self.provider.endpoints.websocket_url}?key={quote(api_key)}"
        connection = await self.transport.aconnect(url)
        setup = GeminiLiveConfigMapper().map(self.name, config)
        return await GeminiLiveSession.create(connection, setup)
