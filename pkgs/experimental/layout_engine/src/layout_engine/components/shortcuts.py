from __future__ import annotations
from typing import Mapping, Any
from .spec import ComponentSpec
from .default import Component, ComponentRegistry


def define_component(
    *,
    role: str,
    module: str,
    export: str = "default",
    version: str | None = None,
    defaults: Mapping[str, Any] | None = None,
) -> ComponentSpec:
    """Return a ComponentSpec (no registration side-effects)."""
    return ComponentSpec(
        role=role,
        module=module,
        export=export,
        version=version,
        defaults=defaults or {},
    )


def derive_component(base: ComponentSpec, **overrides) -> ComponentSpec:
    """Immutable copy of a ComponentSpec with field overrides."""
    if hasattr(base, "model_dump"):
        data = base.model_dump()
    else:
        data = base.dict()
    data.update(overrides)
    return ComponentSpec(**data)


def make_component(spec: ComponentSpec) -> Component:
    """Instantiate a default Component from a spec."""
    return Component(spec=spec)


def use_component(registry: ComponentRegistry, role: str) -> Component:
    """Convenience accessor that wraps a registry lookup in a Component."""
    spec = registry.get(role)
    return Component(spec=spec)


def apply_defaults(
    registry: ComponentRegistry, role: str, overrides: Mapping[str, Any] | None = None
) -> dict:
    """Resolve component props by merging defaults with optional overrides."""
    component = use_component(registry, role)
    return component.resolve_props(overrides)
