from __future__ import annotations

from typing import Iterable, Mapping

from layout_engine import AtomRegistry, AtomSpec

from .default import AtomPresetCatalog
from .spec import AtomPreset


def presets_from_specs(specs: Iterable[AtomSpec]) -> dict[str, AtomPreset]:
    """Convert raw :class:`AtomSpec` entries into :class:`AtomPreset` models."""
    return {
        spec.role: AtomPreset(
            role=spec.role,
            module=spec.module,
            export=spec.export,
            version=spec.version,
            defaults=dict(spec.defaults),
        )
        for spec in specs
    }


def load_catalog(
    data: Mapping[str, AtomPreset] | Iterable[AtomPreset],
) -> AtomPresetCatalog:
    """Instantiate a catalog from raw preset data."""
    return AtomPresetCatalog(data)


def build_registry(
    presets: Mapping[str, AtomPreset] | Iterable[AtomPreset],
) -> AtomRegistry:
    """Create an :class:`AtomRegistry` populated with the provided presets."""
    return load_catalog(presets).build_registry()
