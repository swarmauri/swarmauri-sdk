from typing import Any, Literal

from swarmauri_base.model_providers.ProviderErrorMapperBase import (
    ProviderErrorMapperBase,
)
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ProviderErrorMapperBase, "QwenErrorMapper")
class QwenErrorMapper(ProviderErrorMapperBase):
    type: Literal["QwenErrorMapper"] = "QwenErrorMapper"

    def map_error(self, error: BaseException | Any) -> BaseException:
        return RuntimeError(f"Qwen provider error: {error}")
