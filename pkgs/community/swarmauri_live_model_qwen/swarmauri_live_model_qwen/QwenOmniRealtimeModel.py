from typing import Any, Literal

from pydantic import ConfigDict, Field
from swarmauri_base.live_models.LiveCapabilitiesBase import (
    LiveCapabilitiesBase,
)
from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_base.live_models.LiveModelBase import LiveModelBase
from swarmauri_provider_qwen import QwenProvider
from swarmauri_transport_websocket import WebSocketClient

from .QwenOmniRealtimeConfigMapper import QwenOmniRealtimeConfigMapper
from .QwenOmniRealtimeSession import QwenOmniRealtimeSession


class QwenOmniRealtimeModel(LiveModelBase):
    name: str = "qwen-omni-turbo-realtime"
    provider: QwenProvider = Field(default_factory=QwenProvider)
    transport: Any = Field(default_factory=WebSocketClient, exclude=True)
    capabilities: LiveCapabilitiesBase = Field(
        default_factory=lambda: LiveCapabilitiesBase(
            input_modalities=frozenset({"text", "audio", "image"}),
            output_modalities=frozenset({"text", "audio"}),
            features=frozenset({"tools", "transcription"}),
            session_features=frozenset({"realtime"}),
        )
    )
    type: Literal["QwenOmniRealtimeModel"] = "QwenOmniRealtimeModel"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    async def aconnect(self, config: LiveConfigBase):
        connection_config = self.provider.prepare_connection(
            "realtime.connect", model=self.name
        )
        connection = await self.transport.aconnect(
            connection_config.resolved_url(),
            headers=connection_config.headers,
        )
        return await QwenOmniRealtimeSession.create(
            connection, QwenOmniRealtimeConfigMapper().map(config)
        )
