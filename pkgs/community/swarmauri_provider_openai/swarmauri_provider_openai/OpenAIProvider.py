from typing import Any, Dict, Literal

from pydantic import Field, model_validator

from swarmauri_base.model_providers import ModelProviderBase

from .OpenAIEndpoints import OpenAIEndpoints
from .OpenAIErrorMapper import OpenAIErrorMapper
from .OpenAIModelCatalog import OpenAIModelCatalog


class OpenAIProvider(ModelProviderBase):
    provider_name: Literal["openai"] = "openai"
    endpoints: OpenAIEndpoints = Field(default_factory=OpenAIEndpoints)
    catalog: OpenAIModelCatalog = Field(default_factory=OpenAIModelCatalog)
    error_mapper: OpenAIErrorMapper = Field(default_factory=OpenAIErrorMapper)
    type: Literal["OpenAIProvider"] = "OpenAIProvider"

    @model_validator(mode="after")
    def configure(self) -> "OpenAIProvider":
        self.base_url = self.base_url or self.endpoints.base_url
        if self.organization:
            self.default_headers.setdefault(
                "OpenAI-Organization", self.organization
            )
        if self.project:
            self.default_headers.setdefault("OpenAI-Project", self.project)
        return self

    def connection_options(self) -> Dict[str, Any]:
        options = super().connection_options()
        if self.api_key is not None:
            options["api_key"] = self.api_key.get_secret_value()
        return options
