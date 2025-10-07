"""Atomic component registry for tiles (framework-agnostic).

- ComponentSpec defines how a tile role maps to a client module/export and default props.
- ComponentRegistry stores ComponentSpec entries and can resolve merged props.
- bindings provides JSON (de)serialization and optional server-side render bindings (html/svg).
"""

from .spec import ComponentSpec, merge_props, validate_role, validate_module
from .base import IComponentRegistry
from .default import ComponentRegistry, Component
from .shortcuts import define_component, use_component, apply_defaults
from .decorators import component, validate_props
from .bindings import (
    to_dict,
    from_dict,
    registry_to_dict,
    registry_from_dict,
    ServerBindings,
    Renderer,
    HTMLRenderer,
    SVGRenderer,
)

__all__ = [
    "ComponentSpec",
    "merge_props",
    "validate_role",
    "validate_module",
    "IComponentRegistry",
    "Component",
    "ComponentRegistry",
    "define_component",
    "use_component",
    "apply_defaults",
    "component",
    "validate_props",
    "to_dict",
    "from_dict",
    "registry_to_dict",
    "registry_from_dict",
    "ServerBindings",
    "Renderer",
    "HTMLRenderer",
    "SVGRenderer",
]

from .shortcuts import (
    derive_component as _derive_component,
    make_component as _make_component,
)
from .decorators import component_ctx as _component_ctx

derive_component = _derive_component
make_component = _make_component
component_ctx = _component_ctx

__all__ = list(
    set(
        [
            *(globals().get("__all__", [])),
            "Component",
            "define_component",
            "derive_component",
            "make_component",
            "component_ctx",
        ]
    )
)
