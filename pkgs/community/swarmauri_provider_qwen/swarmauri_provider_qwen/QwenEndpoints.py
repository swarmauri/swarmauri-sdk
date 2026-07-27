from typing import Literal
from swarmauri_base.model_providers.ProviderEndpointBase import (
    ProviderEndpointBase,
)


class QwenEndpoints(ProviderEndpointBase):
    base_url: str = "https://dashscope-intl.aliyuncs.com/api/v1"
    websocket_url: str = "wss://dashscope-intl.aliyuncs.com/api-ws/v1/realtime"
    type: Literal["QwenEndpoints"] = "QwenEndpoints"
