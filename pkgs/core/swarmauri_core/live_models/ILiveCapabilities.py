"""Live-model capability interface."""

from abc import ABC

from swarmauri_core.models.IModelCapabilities import IModelCapabilities


class ILiveCapabilities(IModelCapabilities, ABC):
    session_features: frozenset[str]
