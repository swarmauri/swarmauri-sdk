from __future__ import annotations

from typing import Iterable, Mapping

from layout_engine import AtomRegistry, AtomSpec

from .spec import AtomPreset


class AtomPresetCatalog:
    """In-memory catalog backed by a mapping or iterable of presets."""

    def __init__(self, presets: Mapping[str, AtomPreset] | Iterable[AtomPreset]):
        if isinstance(presets, Mapping):
            self._presets = dict(presets)
        else:
            self._presets = {preset.role: preset for preset in presets}

    def presets(self) -> tuple[AtomPreset, ...]:
        return tuple(self._presets.values())

    def get(self, role: str) -> AtomPreset:
        try:
            return self._presets[role]
        except KeyError as exc:
            raise KeyError(f"Unknown atom preset role: {role}") from exc

    def as_specs(self) -> dict[str, AtomSpec]:
        return {role: preset.to_spec() for role, preset in self._presets.items()}

    def build_registry(self) -> AtomRegistry:
        registry = AtomRegistry()
        registry.register_many(self.as_specs().values())
        return registry
