from typing import Any, Literal

from swarmauri_base.model_providers.ProviderErrorMapperBase import (
    ProviderErrorMapperBase,
)


class OpenRouterErrorMapper(ProviderErrorMapperBase):
    type: Literal["OpenRouterErrorMapper"] = "OpenRouterErrorMapper"

    def map_error(self, error: BaseException | Any) -> BaseException:
        return RuntimeError(f"OpenRouter provider error: {error}")
