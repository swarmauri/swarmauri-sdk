from typing import Any, Literal

from swarmauri_base.model_providers.ProviderErrorMapperBase import (
    ProviderErrorMapperBase,
)
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ProviderErrorMapperBase, "AmazonNovaErrorMapper")
class AmazonNovaErrorMapper(ProviderErrorMapperBase):
    type: Literal["AmazonNovaErrorMapper"] = "AmazonNovaErrorMapper"

    def map_error(self, error: BaseException | Any) -> BaseException:
        return RuntimeError(f"Amazon Nova provider error: {error}")
