from typing import Literal
from swarmauri_base.model_providers import ProviderEndpointBase


class XAIEndpoints(ProviderEndpointBase):
    base_url: str = "https://api.x.ai/v1"
    websocket_url: str = "wss://api.x.ai/v1/realtime"
    type: Literal["XAIEndpoints"] = "XAIEndpoints"
