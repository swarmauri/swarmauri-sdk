from __future__ import annotations

import re
from typing import Any, Mapping

from pydantic import BaseModel, Field, ConfigDict, field_validator

_ROLE_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_:-]{1,63}$")
# Approximate ESM specifier sanity check (package or path, may include '@scope/', '.', '/', '-', digits)
_MODULE_RE = re.compile(r"^[a-zA-Z0-9@_./\-][a-zA-Z0-9@_./\-]*$")


def validate_atom_role(role: str) -> str:
    if not _ROLE_RE.match(role):
        raise ValueError(
            f"invalid atom role '{role}' (allowed: [A-Za-z][A-Za-z0-9_:-] 2..64)"
        )
    return role


def validate_atom_module(module: str) -> str:
    if not _MODULE_RE.match(module):
        raise ValueError(f"invalid module specifier '{module}'")
    return module


def merge_atom_props(
    defaults: Mapping[str, Any], overrides: Mapping[str, Any] | None
) -> dict:
    """Shallow-merge atom defaults with overrides (overrides win)."""
    out = dict(defaults or {})
    if overrides:
        out.update(overrides)
    return out


class AtomSpec(BaseModel):
    """Declarative mapping for a tile role to an atom module/export.

    - role: semantic name used by tiles (e.g., 'kpi','timeseries','map','table')
    - module: ESM specifier (resolved by import-map) for Svelte/Vue/React host
    - export: named export to load (default: 'default')
    - version: atom version tag for cache-busting/telemetry
    - defaults: default props merged at compile/manifest time
    """

    model_config = ConfigDict(frozen=True)

    role: str
    module: str
    export: str = "default"
    version: str = "1.0.0"
    defaults: Mapping[str, Any] = Field(default_factory=dict)

    @field_validator("role")
    @classmethod
    def _validate_role(cls, value: str) -> str:
        return validate_atom_role(value)

    @field_validator("module")
    @classmethod
    def _validate_module(cls, value: str) -> str:
        return validate_atom_module(value)

    @field_validator("defaults", mode="before")
    @classmethod
    def _coerce_defaults(cls, value: Mapping[str, Any] | None) -> Mapping[str, Any]:
        return dict(value or {})

    def with_overrides(self, **fields: Any) -> AtomSpec:
        return self.model_copy(update=fields)
