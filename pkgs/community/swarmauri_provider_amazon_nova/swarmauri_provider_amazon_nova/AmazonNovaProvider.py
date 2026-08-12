from typing import Literal
from urllib.parse import quote

from pydantic import Field, SecretStr, model_validator
from swarmauri_base.model_providers.ModelProviderBase import ModelProviderBase
from swarmauri_base.model_providers.ProviderConnectionConfig import (
    ProviderConnectionConfig,
)

from .AmazonNovaAuthConfig import AmazonNovaAuthConfig
from .AmazonNovaEndpoints import AmazonNovaEndpoints
from .AmazonNovaErrorMapper import AmazonNovaErrorMapper
from .AmazonNovaModelCatalog import AmazonNovaModelCatalog


class AmazonNovaProvider(ModelProviderBase):
    provider_name: Literal["amazon_nova"] = "amazon_nova"
    access_key_id: SecretStr | None = Field(default=None, exclude=True)
    secret_access_key: SecretStr | None = Field(default=None, exclude=True)
    session_token: SecretStr | None = Field(default=None, exclude=True)
    profile: str | None = None
    auth: AmazonNovaAuthConfig = Field(
        default_factory=AmazonNovaAuthConfig, exclude=True
    )
    endpoints: AmazonNovaEndpoints = Field(default_factory=AmazonNovaEndpoints)
    catalog: AmazonNovaModelCatalog = Field(
        default_factory=AmazonNovaModelCatalog
    )
    error_mapper: AmazonNovaErrorMapper = Field(
        default_factory=AmazonNovaErrorMapper
    )
    type: Literal["AmazonNovaProvider"] = "AmazonNovaProvider"

    @model_validator(mode="after")
    def configure(self) -> "AmazonNovaProvider":
        self.region = self.region or self.endpoints.region
        self.endpoints.region = self.region
        self.base_url = self.base_url or self.endpoints.resolve(
            "bedrock.runtime"
        )
        if self.access_key_id is not None:
            self.auth.access_key_id = self.access_key_id
        elif self.auth.access_key_id is not None:
            self.access_key_id = self.auth.access_key_id
        if self.secret_access_key is not None:
            self.auth.secret_access_key = self.secret_access_key
        elif self.auth.secret_access_key is not None:
            self.secret_access_key = self.auth.secret_access_key
        if self.session_token is not None:
            self.auth.session_token = self.session_token
        elif self.auth.session_token is not None:
            self.session_token = self.auth.session_token
        if self.profile is not None:
            self.auth.profile = self.profile
        elif self.auth.profile is not None:
            self.profile = self.auth.profile
        return self

    def connection_config(
        self, capability: str, model: str | None = None
    ) -> ProviderConnectionConfig:
        endpoint = self.endpoints.resolve(capability)
        options: dict[str, object] = {"region": self.region}
        if self.profile is not None:
            options["profile"] = self.profile
        if model is not None:
            options["model_id"] = model
            endpoint = (
                f"{endpoint.rstrip('/')}/model/{quote(model, safe='')}"
                "/invoke-with-bidirectional-stream"
            )
        return ProviderConnectionConfig(
            endpoint=endpoint,
            transport_options=options,
            auth_context=self.auth,
        )

    def prepare_connection(
        self, capability: str, model: str | None = None
    ) -> ProviderConnectionConfig:
        config = super().prepare_connection(capability, model)
        options = dict(config.transport_options)
        options.update(self.auth.sdk_credentials())
        return config.model_copy(update={"transport_options": options})
