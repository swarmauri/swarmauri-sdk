from typing import Any, Literal

from swarmauri_base.model_providers.ProviderErrorMapperBase import (
    ProviderErrorMapperBase,
)
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ProviderErrorMapperBase, "GeminiErrorMapper")
class GeminiErrorMapper(ProviderErrorMapperBase):
    type: Literal["GeminiErrorMapper"] = "GeminiErrorMapper"

    def map_error(self, error: BaseException | Any) -> BaseException:
        if isinstance(error, BaseException):
            return RuntimeError(f"Gemini provider error: {error}")
        return RuntimeError(f"Gemini provider error: {error}")
