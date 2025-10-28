from __future__ import annotations

from typing import Iterable, Mapping

from layout_engine import AtomRegistry, AtomSpec

from ..swarma import SwarmaAtom, VUE_BUTTON

FRAMEWORK = "vue"

DEFAULT_PRESETS: dict[str, SwarmaAtom] = {
    VUE_BUTTON.spec.role: VUE_BUTTON,
}

DEFAULT_ATOMS: dict[str, AtomSpec] = {
    role: atom.to_spec() for role, atom in DEFAULT_PRESETS.items()
}

ATOM_TABLE = [
    {
        "role": atom.spec.role,
        "framework": FRAMEWORK,
        "module": atom.spec.module,
        "export": atom.spec.export,
        "version": atom.spec.version,
        "defaults": dict(atom.spec.defaults),
    }
    for atom in DEFAULT_PRESETS.values()
]


def build_registry(
    *,
    extra_presets: Iterable[SwarmaAtom] | Mapping[str, SwarmaAtom] | None = None,
    overrides: Mapping[str, Mapping[str, object]] | None = None,
) -> AtomRegistry:
    """Create an AtomRegistry populated with SwarmaKit Vue presets."""

    presets: dict[str, SwarmaAtom] = dict(DEFAULT_PRESETS)

    if extra_presets:
        if isinstance(extra_presets, Mapping):
            presets.update(extra_presets)
        else:
            presets.update({atom.spec.role: atom for atom in extra_presets})

    if overrides:
        for role, patch in overrides.items():
            if role not in presets:
                continue
            presets[role] = presets[role].with_overrides(**patch)

    registry = AtomRegistry()
    registry.register_many(atom.to_spec() for atom in presets.values())
    return registry


__all__ = ["FRAMEWORK", "DEFAULT_PRESETS", "DEFAULT_ATOMS", "ATOM_TABLE", "build_registry"]
