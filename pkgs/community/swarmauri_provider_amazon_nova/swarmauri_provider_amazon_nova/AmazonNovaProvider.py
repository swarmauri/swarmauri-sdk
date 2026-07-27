from typing import Any, Dict, Literal, Optional

from pydantic import Field, SecretStr, model_validator

from swarmauri_base.model_providers import ModelProviderBase

from .AmazonNovaEndpoints import AmazonNovaEndpoints
from .AmazonNovaErrorMapper import AmazonNovaErrorMapper
from .AmazonNovaModelCatalog import AmazonNovaModelCatalog


class AmazonNovaProvider(ModelProviderBase):
    provider_name: Literal["amazon_nova"] = "amazon_nova"
    access_key_id: Optional[SecretStr] = Field(default=None, exclude=True)
    secret_access_key: Optional[SecretStr] = Field(default=None, exclude=True)
    session_token: Optional[SecretStr] = Field(default=None, exclude=True)
    profile: Optional[str] = None
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
        self.base_url = self.base_url or self.endpoints.runtime_url()
        return self

    def connection_options(self) -> Dict[str, Any]:
        options = super().connection_options()
        options.update({"region": self.region, "profile": self.profile})
        for name in ("access_key_id", "secret_access_key", "session_token"):
            secret = getattr(self, name)
            if secret is not None:
                options[name] = secret.get_secret_value()
        return options
