from typing import Literal

from swarmauri_base.model_providers import ProviderEndpointBase


class OpenAIEndpoints(ProviderEndpointBase):
    base_url: str = "https://api.openai.com/v1"
    realtime_url: str = "wss://api.openai.com/v1/realtime"
    responses_websocket_url: str = "wss://api.openai.com/v1/responses"
    type: Literal["OpenAIEndpoints"] = "OpenAIEndpoints"
