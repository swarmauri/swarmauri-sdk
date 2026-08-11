from typing import Any, Literal

from pydantic import Field, model_validator
from swarmauri_base.model_providers.ModelProviderBase import ModelProviderBase
from swarmauri_base.model_providers.ProviderConnectionConfigBase import (
    ProviderConnectionConfigBase,
)

from .XAIAuthConfig import XAIAuthConfig
from .XAIEndpoints import XAIEndpoints
from .XAIErrorMapper import XAIErrorMapper
from .XAIModelCatalog import XAIModelCatalog


class XAIProvider(ModelProviderBase):
    provider_name: Literal["xai"] = "xai"
    endpoints: XAIEndpoints = Field(default_factory=XAIEndpoints)
    catalog: XAIModelCatalog = Field(default_factory=XAIModelCatalog)
    error_mapper: XAIErrorMapper = Field(default_factory=XAIErrorMapper)
    auth: XAIAuthConfig = Field(default_factory=XAIAuthConfig, exclude=True)
    type: Literal["XAIProvider"] = "XAIProvider"

    @model_validator(mode="after")
    def configure(self) -> "XAIProvider":
        self.base_url = self.base_url or self.endpoints.base_url
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

    def connection_config(
        self,
        capability: str,
        model: str | None = None,
    ) -> ProviderConnectionConfigBase:
        endpoints = {
            "chat.completions": self.endpoints.resolve(
                self.endpoints.chat_completions_path
            ),
            "models.list": self.endpoints.resolve(self.endpoints.models_path),
            "realtime.connect": self.endpoints.websocket_url,
        }
        try:
            endpoint = endpoints[capability]
        except KeyError as error:
            raise ValueError(
                f"xAI does not support capability {capability!r}"
            ) from error
        # Keep credentials in the excluded auth context. The legacy
        # connection_options method still exposes api_key for existing live
        # model consumers, but connection configurations must serialize safely.
        options = super().connection_options()
        if model is not None:
            options["model"] = model
        return ProviderConnectionConfigBase(
            endpoint=endpoint,
            headers={
                **self.default_headers,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            transport_options=options,
            auth_context=self.auth,
        )

    @staticmethod
    def authorize(config: ProviderConnectionConfigBase) -> dict[str, str]:
        auth = config.auth_context
        if not isinstance(auth, XAIAuthConfig):
            raise TypeError("xAI connection configuration has no auth context")
        return auth.apply(config.headers)
