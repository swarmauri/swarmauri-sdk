"""Atomic component registry for tiles (framework-agnostic).

- ComponentSpec defines how a tile role maps to a client module/export and default props.
- ComponentRegistry stores ComponentSpec entries and can resolve merged props.
- bindings provides JSON (de)serialization and optional server-side render bindings (html/svg).
"""
from .spec import ComponentSpec, merge_props, validate_role, validate_module
from .base import IComponentRegistry
from .default import ComponentRegistry
from .shortcuts import define_component, use_component, apply_defaults
from .decorators import component, validate_props
from .bindings import (
    to_dict, from_dict,
    registry_to_dict, registry_from_dict,
    ServerBindings, Renderer, HTMLRenderer, SVGRenderer
)

__all__ = [
    "ComponentSpec", "merge_props", "validate_role", "validate_module",
    "IComponentRegistry", "ComponentRegistry",
    "define_component", "use_component", "apply_defaults",
    "component", "validate_props",
    "to_dict", "from_dict", "registry_to_dict", "registry_from_dict",
    "ServerBindings", "Renderer", "HTMLRenderer", "SVGRenderer",
]
