from typing import Literal

from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase

from .OpenAIRealtimeModel import OpenAIRealtimeModel
from .OpenAIRealtimeSession import OpenAIRealtimeSession


class OpenAIResponsesWSModel(OpenAIRealtimeModel):
    type: Literal["OpenAIResponsesWSModel"] = "OpenAIResponsesWSModel"

    async def aconnect(self, config: LiveConfigBase) -> OpenAIRealtimeSession:
        connection_config = self.provider.prepare_connection(
            "responses.connect", model=self.name
        )
        connection = await self.transport.aconnect(
            connection_config.resolved_url(),
            headers=connection_config.headers,
        )
        return await OpenAIRealtimeSession.create(connection)
