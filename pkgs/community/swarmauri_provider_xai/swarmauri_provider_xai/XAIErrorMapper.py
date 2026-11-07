from typing import Any, Literal

from swarmauri_base.model_providers.ProviderErrorMapperBase import (
    ProviderErrorMapperBase,
)


class XAIErrorMapper(ProviderErrorMapperBase):
    type: Literal["XAIErrorMapper"] = "XAIErrorMapper"

    def map_error(self, error: BaseException | Any) -> BaseException:
        return RuntimeError(f"xAI provider error: {error}")
