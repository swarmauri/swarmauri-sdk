from typing import Any, Literal

from pydantic import Field, model_validator
from swarmauri_base.model_providers.ModelProviderBase import ModelProviderBase

from .QwenAuthConfig import QwenAuthConfig
from .QwenEndpoints import QwenEndpoints
from .QwenErrorMapper import QwenErrorMapper
from .QwenModelCatalog import QwenModelCatalog


class QwenProvider(ModelProviderBase):
    provider_name: Literal["qwen"] = "qwen"
    endpoints: QwenEndpoints = Field(default_factory=QwenEndpoints)
    auth: QwenAuthConfig = Field(default_factory=QwenAuthConfig, exclude=True)
    catalog: QwenModelCatalog = Field(default_factory=QwenModelCatalog)
    error_mapper: QwenErrorMapper = Field(default_factory=QwenErrorMapper)
    type: Literal["QwenProvider"] = "QwenProvider"

    @model_validator(mode="after")
    def configure(self) -> "QwenProvider":
        self.base_url = self.base_url or self.endpoints.resolve("api")
        self.endpoints.base_url = self.base_url
        if self.api_key is not None:
            self.auth.api_key = self.api_key
        elif self.auth.api_key is not None:
            self.api_key = self.auth.api_key
        return self

    def connection_options(self) -> dict[str, Any]:
        options = super().connection_options()
        if self.api_key:
            options["api_key"] = self.api_key.get_secret_value()
        return options
