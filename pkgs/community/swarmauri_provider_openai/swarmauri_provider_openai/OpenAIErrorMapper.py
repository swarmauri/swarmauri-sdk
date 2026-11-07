from typing import Any, Literal

from swarmauri_base.model_providers.ProviderErrorMapperBase import (
    ProviderErrorMapperBase,
)
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ProviderErrorMapperBase, "OpenAIErrorMapper")
class OpenAIErrorMapper(ProviderErrorMapperBase):
    type: Literal["OpenAIErrorMapper"] = "OpenAIErrorMapper"

    def map_error(self, error: BaseException | Any) -> BaseException:
        return RuntimeError(f"OpenAI provider error: {error}")
