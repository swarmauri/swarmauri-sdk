from typing import Literal

from swarmauri_base.model_providers.ProviderEndpointBase import (
    ProviderEndpointBase,
)


class QwenEndpoints(ProviderEndpointBase):
    base_url: str = "https://dashscope-intl.aliyuncs.com/api/v1"
    websocket_url: str = "wss://dashscope-intl.aliyuncs.com/api-ws/v1/realtime"
    type: Literal["QwenEndpoints"] = "QwenEndpoints"

    def resolve(self, capability: str) -> str:
        endpoints = {
            "api": self.base_url,
            "realtime.connect": self.websocket_url,
        }
        try:
            return endpoints[capability]
        except KeyError as error:
            raise ValueError(
                f"Qwen does not support capability {capability!r}"
            ) from error
