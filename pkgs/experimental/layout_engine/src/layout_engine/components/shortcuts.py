from __future__ import annotations
from typing import Mapping, Any
from .spec import ComponentSpec
from .default import Component
from .registry import ComponentRegistry  # if present; otherwise import from __init__

def define_component(*, role: str, module: str, export: str = "default",
                     version: str | None = None, defaults: Mapping[str, Any] | None = None) -> ComponentSpec:
    """Return a ComponentSpec (no registration side-effects)."""
    return ComponentSpec(role=role, module=module, export=export, version=version, defaults=defaults or {})

def derive_component(base: ComponentSpec, **overrides) -> ComponentSpec:
    """Immutable copy of a ComponentSpec with field overrides."""
    data = base.dict()
    data.update(overrides)
    return ComponentSpec(**data)

def make_component(spec: ComponentSpec) -> Component:
    """Instantiate a default Component from a spec."""
    return Component(spec=spec)
