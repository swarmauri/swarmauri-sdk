from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Mapping, TypeVar, Type

from layout_engine import AtomRegistry, AtomSpec

from .spec import AtomPreset


class IAtomCatalog(ABC):
    """Core interface for atom preset catalogs."""

    @abstractmethod
    def presets(self) -> Iterable[AtomPreset]:
        """Return the presets provided by the catalog."""
        raise NotImplementedError

    def as_specs(self) -> dict[str, AtomSpec]:
        """Materialize presets as a ``role -> AtomSpec`` mapping."""
        return {preset.role: preset.to_spec() for preset in self.presets()}

    def build_registry(self) -> AtomRegistry:
        """Create an :class:`AtomRegistry` primed with the catalog presets."""
        registry = AtomRegistry()
        registry.register_many(self.as_specs().values())
        return registry


CatalogT = TypeVar("CatalogT", bound="AtomPresetCatalog")


class AtomPresetCatalog(IAtomCatalog):
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

    @classmethod
    def from_specs(cls: Type[CatalogT], specs: Iterable[AtomSpec]) -> CatalogT:
        """Instantiate a catalog from raw :class:`AtomSpec` entries."""
        presets = {
            spec.role: AtomPreset(
                role=spec.role,
                module=spec.module,
                export=spec.export,
                version=spec.version,
                defaults=dict(spec.defaults),
            )
            for spec in specs
        }
        return cls(presets)
