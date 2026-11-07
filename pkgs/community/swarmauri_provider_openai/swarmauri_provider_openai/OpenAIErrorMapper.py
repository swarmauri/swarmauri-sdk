from typing import Any, Literal

from swarmauri_base.model_providers.ProviderErrorMapperBase import (
    ProviderErrorMapperBase,
)


class OpenAIErrorMapper(ProviderErrorMapperBase):
    type: Literal["OpenAIErrorMapper"] = "OpenAIErrorMapper"

    def map_error(self, error: BaseException | Any) -> BaseException:
        return RuntimeError(f"OpenAI provider error: {error}")
