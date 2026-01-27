from __future__ import annotations

from typing import Any, Iterable, Mapping, Optional

from .spec import AtomSpec, merge_atom_props


class AtomRegistry:
    """In-memory registry keyed by atom role (case-sensitive)."""

    def __init__(self):
        self._by_role: dict[str, AtomSpec] = {}

    # --- CRUD ---
    def register(self, spec: AtomSpec) -> None:
        role = spec.role
        if role in self._by_role:
            raise ValueError(f"Atom role already registered: {role}")
        self._by_role[role] = spec

    def register_many(self, specs: Iterable[AtomSpec]) -> None:
        for s in specs:
            self.register(s)

    def override(self, role: str, /, **fields: Any) -> AtomSpec:
        try:
            base = self._by_role[role]
        except KeyError:
            raise KeyError(f"Unknown atom role: {role}")

        patch = dict(fields)

        merged_fields: dict[str, Any] = {}

        if "defaults" in patch:
            merged = dict(base.defaults)
            merged.update(dict(patch.pop("defaults") or {}))
            merged_fields["defaults"] = merged

        if "tokens" in patch:
            merged_tokens = dict(base.tokens)
            merged_tokens.update(dict(patch.pop("tokens") or {}))
            merged_fields["tokens"] = merged_tokens

        if "registry" in patch:
            merged_registry = dict(base.registry)
            merged_registry.update(dict(patch.pop("registry") or {}))
            merged_fields["registry"] = merged_registry

        merged_fields.update(patch)

        new_spec = base.with_overrides(**merged_fields)
        self._by_role[role] = new_spec
        return new_spec

    # --- Query ---
    def get(self, role: str) -> AtomSpec:
        try:
            return self._by_role[role]
        except KeyError:
            raise KeyError(f"Unknown atom role: {role}")

    def try_get(self, role: str) -> Optional[AtomSpec]:
        return self._by_role.get(role)

    def has(self, role: str) -> bool:
        return role in self._by_role

    def list(self) -> Iterable[AtomSpec]:
        return list(self._by_role.values())

    # --- Resolution ---
    def resolve_props(
        self, role: str, overrides: Mapping[str, Any] | None = None
    ) -> dict:
        spec = self.get(role)
        return merge_atom_props(spec.defaults, overrides)

    # --- (De)serialization ---
    def to_dict(self) -> dict[str, dict]:
        from .bindings import atom_to_dict as _to

        return {role: _to(spec) for role, spec in self._by_role.items()}

    def update_from_dict(self, data: Mapping[str, Mapping[str, Any]]) -> None:
        from .bindings import atom_from_dict as _from

        for role, specd in data.items():
            spec = _from(specd)
            if role != spec.role:
                # ensure role consistency (use key as authority)
                spec = spec.with_overrides(role=role)
            # upsert semantics
            self._by_role[role] = spec

    def dict(self) -> dict[str, dict]:
        """Dict-style alias for serialization helpers."""
        return self.to_dict()

    # --- context manager support ---
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class Atom:
    """Default runtime wrapper around AtomSpec.

    Provides ergonomic accessors and merged props resolution.
    """

    def __init__(self, spec: AtomSpec):
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
        return merge_atom_props(self.spec.defaults, overrides)

    # --- context manager support ---
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False
