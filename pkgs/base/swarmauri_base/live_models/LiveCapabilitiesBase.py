"""Concrete live-model capabilities."""


from pydantic import Field
from swarmauri_core.live_models.ILiveCapabilities import ILiveCapabilities

from swarmauri_base.models.ModelCapabilitiesBase import ModelCapabilitiesBase


class LiveCapabilitiesBase(ModelCapabilitiesBase, ILiveCapabilities):
    session_features: frozenset[str] = Field(default_factory=frozenset)

    def supports(self, feature: str) -> bool:
        return feature in self.features or feature in self.session_features
