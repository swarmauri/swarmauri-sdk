from __future__ import annotations
from typing import Iterable, Mapping, Any, Optional
from .spec import ComponentSpec, merge_props

class ComponentRegistry:
    """In-memory registry keyed by role (case-sensitive)."""
    def __init__(self):
        self._by_role: dict[str, ComponentSpec] = {}

    # --- CRUD ---
    def register(self, spec: ComponentSpec) -> None:
        role = spec.role
        if role in self._by_role:
            raise ValueError(f"Component role already registered: {role}")
        self._by_role[role] = spec

    def register_many(self, specs: Iterable[ComponentSpec]) -> None:
        for s in specs: self.register(s)

    def override(self, role: str, **fields: Any) -> ComponentSpec:
        try:
            base = self._by_role[role]
        except KeyError:
            raise KeyError(f"Unknown component role: {role}")
        new_spec = base.with_overrides(**fields)
        self._by_role[role] = new_spec
        return new_spec

    # --- Query ---
    def get(self, role: str) -> ComponentSpec:
        try:
            return self._by_role[role]
        except KeyError:
            raise KeyError(f"Unknown component role: {role}")

    def try_get(self, role: str) -> Optional[ComponentSpec]:
        return self._by_role.get(role)

    def has(self, role: str) -> bool:
        return role in self._by_role

    def list(self) -> Iterable[ComponentSpec]:
        return list(self._by_role.values())

    # --- Resolution ---
    def resolve_props(self, role: str, overrides: Mapping[str, Any] | None = None) -> dict:
        spec = self.get(role)
        return merge_props(spec.defaults, overrides)

    # --- (De)serialization ---
    def to_dict(self) -> dict[str, dict]:
        from .bindings import to_dict as _to
        return {role: _to(spec) for role, spec in self._by_role.items()}

    def update_from_dict(self, data: Mapping[str, Mapping[str, Any]]) -> None:
        from .bindings import from_dict as _from
        for role, specd in data.items():
            spec = _from(specd)
            if role != spec.role:
                # ensure role consistency (use key as authority)
                spec = spec.with_overrides(role=role)
            # upsert semantics
            self._by_role[role] = spec


    # --- context manager support ---
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        return False

class Component:
    """Default runtime wrapper around ComponentSpec.

    Provides ergonomic accessors and merged props resolution.
    """
    def __init__(self, spec: ComponentSpec):
        self.spec = spec

    @property
    def role(self) -> str:
        return self.spec.role

    @property
    def module(self) -> str:
        return self.spec.module

    @property
    def export(self) -> str:
        return self.spec.export

    @property
    def version(self) -> str:
        return self.spec.version

    def resolve_props(self, overrides: Mapping[str, Any] | None = None) -> dict:
        """Return props merged with registry defaults (spec.defaults ⊕ overrides)."""
        return merge_props(self.spec.defaults, overrides or {})

    # --- context manager support ---
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        return False
