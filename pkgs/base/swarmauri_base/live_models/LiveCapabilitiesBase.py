"""Concrete live-model capabilities."""

from typing import FrozenSet

from pydantic import Field

from swarmauri_base.models.ModelCapabilitiesBase import ModelCapabilitiesBase
from swarmauri_core.live_models.ILiveCapabilities import ILiveCapabilities


class LiveCapabilitiesBase(ModelCapabilitiesBase, ILiveCapabilities):
    session_features: FrozenSet[str] = Field(default_factory=frozenset)

    def supports(self, feature: str) -> bool:
        return feature in self.features or feature in self.session_features
