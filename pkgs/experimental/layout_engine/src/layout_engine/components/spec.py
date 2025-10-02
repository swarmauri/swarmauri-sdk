from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Any, Mapping
import re

_ROLE_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_:-]{1,63}$")
# Approximate ESM specifier sanity check (package or path, may include '@scope/', '.', '/', '-', digits)
_MODULE_RE = re.compile(r"^[a-zA-Z0-9@_./\-][a-zA-Z0-9@_./\-]*$")

def validate_role(role: str) -> str:
    if not _ROLE_RE.match(role):
        raise ValueError(f"invalid component role '{role}' (allowed: [A-Za-z][A-Za-z0-9_:-] 2..64)")
    return role

def validate_module(module: str) -> str:
    if not _MODULE_RE.match(module):
        raise ValueError(f"invalid module specifier '{module}'")
    return module

def merge_props(defaults: Mapping[str, Any], overrides: Mapping[str, Any] | None) -> dict:
    """Shallow-merge defaults with overrides (overrides win)."""
    out = dict(defaults or {})
    if overrides:
        out.update(overrides)
    return out

@dataclass(frozen=True)
class ComponentSpec:
    """Declarative mapping for a tile role to a client module/export.

    - role: semantic name used by tiles (e.g., 'kpi','timeseries','map','table')
    - module: ESM specifier (resolved by import-map) for Svelte/Vue/React host
    - export: named export to load (default: 'default')
    - version: component version tag for cache-busting/telemetry
    - defaults: default props merged at compile/manifest time
    """
    role: str
    module: str
    export: str = "default"
    version: str = "1.0.0"
    defaults: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # validate
        validate_role(self.role)
        validate_module(self.module)

    def with_overrides(self, **fields: Any) -> "ComponentSpec":
        """Return a new ComponentSpec with specific fields replaced."""
        return replace(self, **fields)

    def props(self, overrides: Mapping[str, Any] | None = None) -> dict:
        """Return merged props (defaults ⊕ overrides)."""
        return merge_props(self.defaults, overrides or {})
