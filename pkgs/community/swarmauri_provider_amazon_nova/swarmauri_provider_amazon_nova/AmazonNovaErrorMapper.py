from typing import Any, Literal
from swarmauri_base.model_providers.ProviderErrorMapperBase import (
    ProviderErrorMapperBase,
)


class AmazonNovaErrorMapper(ProviderErrorMapperBase):
    type: Literal["AmazonNovaErrorMapper"] = "AmazonNovaErrorMapper"

    def map_error(self, error: BaseException | Any) -> BaseException:
        return RuntimeError(f"Amazon Nova provider error: {error}")
