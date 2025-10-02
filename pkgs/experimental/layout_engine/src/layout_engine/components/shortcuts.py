from __future__ import annotations
from typing import Mapping, Any
from .spec import ComponentSpec, merge_props
from .default import ComponentRegistry

def define_component(registry: ComponentRegistry, *, role: str, module: str,
                     export: str = "default", version: str = "1.0.0",
                     defaults: Mapping[str, Any] | None = None) -> ComponentSpec:
    spec = ComponentSpec(role=role, module=module, export=export, version=version, defaults=defaults or {})
    registry.register(spec)
    return spec

def use_component(registry: ComponentRegistry, role: str) -> ComponentSpec:
    return registry.get(role)

def apply_defaults(spec: ComponentSpec, overrides: Mapping[str, Any] | None = None) -> dict:
    return merge_props(spec.defaults, overrides or {})
