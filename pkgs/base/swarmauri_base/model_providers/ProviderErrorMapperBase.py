"""Default provider error mapping behavior."""

from typing import Any, Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.model_providers.IProviderErrorMapper import (
    IProviderErrorMapper,
)


class ProviderErrorMapperBase(IProviderErrorMapper, ComponentBase):
    type: Literal["ProviderErrorMapperBase"] = "ProviderErrorMapperBase"

    def map_error(self, error: BaseException | Any) -> BaseException:
        if isinstance(error, BaseException):
            return error
        return RuntimeError(str(error))
