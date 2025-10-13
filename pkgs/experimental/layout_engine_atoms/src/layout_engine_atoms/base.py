from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from layout_engine import AtomSpec, AtomRegistry

from .spec import AtomPreset


class IAtomPresetCatalog(ABC):
    """Abstract interface for loading atom presets."""

    @abstractmethod
    def presets(self) -> Iterable[AtomPreset]:
        raise NotImplementedError

    def as_specs(self) -> dict[str, AtomSpec]:
        """Materialize presets as a ``role -> AtomSpec`` mapping."""
        return {preset.role: preset.to_spec() for preset in self.presets()}

    def build_registry(self) -> AtomRegistry:
        """Create an :class:`AtomRegistry` primed with the catalog presets."""
        registry = AtomRegistry()
        registry.register_many(self.presets_to_specs())
        return registry

    def presets_to_specs(self) -> Iterable[AtomSpec]:
        return (preset.to_spec() for preset in self.presets())
