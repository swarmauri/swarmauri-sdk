"""Common base for model resources."""

from typing import Literal, Optional

from pydantic import ConfigDict, Field, SecretStr

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.model_providers.ModelProviderBase import ModelProviderBase
from swarmauri_core.models.IModel import IModel

from .ModelCapabilitiesBase import ModelCapabilitiesBase


@ComponentBase.register_model()
class ModelBase(IModel, ComponentBase):
    name: str = ""
    provider: Optional[ModelProviderBase] = None
    capabilities: ModelCapabilitiesBase = Field(
        default_factory=ModelCapabilitiesBase
    )
    api_key: Optional[SecretStr] = Field(default=None, exclude=True)
    timeout: float = Field(default=600.0, gt=0)
    max_retries: int = Field(default=3, ge=0)
    retry_delay: float = Field(default=2.0, ge=0)
    resource: str = Field(default=ResourceTypes.MODEL.value, frozen=True)
    type: Literal["ModelBase"] = "ModelBase"
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)
