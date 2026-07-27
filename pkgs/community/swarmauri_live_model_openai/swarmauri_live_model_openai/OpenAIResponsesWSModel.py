from typing import Literal

from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase

from .OpenAIRealtimeModel import OpenAIRealtimeModel
from .OpenAIRealtimeSession import OpenAIRealtimeSession


class OpenAIResponsesWSModel(OpenAIRealtimeModel):
    type: Literal["OpenAIResponsesWSModel"] = "OpenAIResponsesWSModel"

    async def aconnect(self, config: LiveConfigBase) -> OpenAIRealtimeSession:
        api_key = self.provider.connection_options().get("api_key")
        if not api_key:
            raise ValueError("OpenAIProvider requires an api_key")
        connection = await self.transport.aconnect(
            self.provider.endpoints.responses_websocket_url,
            headers={"Authorization": f"Bearer {api_key}"},
        )
        return await OpenAIRealtimeSession.create(connection)
