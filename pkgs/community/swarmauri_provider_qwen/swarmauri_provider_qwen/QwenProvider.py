from typing import Any, Dict, Literal
from pydantic import Field, model_validator
from swarmauri_base.model_providers.ModelProviderBase import ModelProviderBase
from .QwenEndpoints import QwenEndpoints
from .QwenErrorMapper import QwenErrorMapper
from .QwenModelCatalog import QwenModelCatalog


class QwenProvider(ModelProviderBase):
    provider_name: Literal["qwen"] = "qwen"
    endpoints: QwenEndpoints = Field(default_factory=QwenEndpoints)
    catalog: QwenModelCatalog = Field(default_factory=QwenModelCatalog)
    error_mapper: QwenErrorMapper = Field(default_factory=QwenErrorMapper)
    type: Literal["QwenProvider"] = "QwenProvider"

    @model_validator(mode="after")
    def configure(self) -> "QwenProvider":
        self.base_url = self.base_url or self.endpoints.base_url
        return self

    def connection_options(self) -> Dict[str, Any]:
        options = super().connection_options()
        if self.api_key:
            options["api_key"] = self.api_key.get_secret_value()
        return options
