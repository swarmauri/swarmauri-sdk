"""Concrete base representation of model capabilities."""


from pydantic import BaseModel, ConfigDict, Field
from swarmauri_core.models.IModelCapabilities import IModelCapabilities


class ModelCapabilitiesBase(IModelCapabilities, BaseModel):
    input_modalities: frozenset[str] = Field(default_factory=frozenset)
    output_modalities: frozenset[str] = Field(default_factory=frozenset)
    features: frozenset[str] = Field(default_factory=frozenset)

    model_config = ConfigDict(frozen=True)

    def supports(self, feature: str) -> bool:
        return feature in self.features
