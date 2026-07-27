"""Concrete base representation of model capabilities."""

from typing import FrozenSet

from pydantic import BaseModel, ConfigDict, Field

from swarmauri_core.models.IModelCapabilities import IModelCapabilities


class ModelCapabilitiesBase(IModelCapabilities, BaseModel):
    input_modalities: FrozenSet[str] = Field(default_factory=frozenset)
    output_modalities: FrozenSet[str] = Field(default_factory=frozenset)
    features: FrozenSet[str] = Field(default_factory=frozenset)

    model_config = ConfigDict(frozen=True)

    def supports(self, feature: str) -> bool:
        return feature in self.features
