from __future__ import annotations
from typing import Any, Mapping

from .spec import AtomSpec
from .default import Atom, AtomRegistry


def define_atom(
    *,
    role: str,
    module: str,
    export: str = "default",
    version: str | None = None,
    defaults: Mapping[str, Any] | None = None,
) -> AtomSpec:
    """Return an AtomSpec (no registration side-effects)."""
    return AtomSpec(
        role=role,
        module=module,
        export=export,
        version=version,
        defaults=defaults or {},
    )


def derive_atom(base: AtomSpec, **overrides) -> AtomSpec:
    """Immutable copy of an AtomSpec with field overrides."""
    if hasattr(base, "model_dump"):
        data = base.model_dump()
    else:
        data = base.dict()
    data.update(overrides)
    return AtomSpec(**data)


def make_atom(spec: AtomSpec) -> Atom:
    """Instantiate a default Atom from a spec."""
    return Atom(spec=spec)


def use_atom(registry: AtomRegistry, role: str) -> Atom:
    """Convenience accessor that wraps a registry lookup in an Atom."""
    spec = registry.get(role)
    return Atom(spec=spec)


def apply_atom_defaults(
    registry: AtomRegistry, role: str, overrides: Mapping[str, Any] | None = None
) -> dict:
    """Resolve atom props by merging defaults with optional overrides."""
    atom = use_atom(registry, role)
    return atom.resolve_props(overrides)
