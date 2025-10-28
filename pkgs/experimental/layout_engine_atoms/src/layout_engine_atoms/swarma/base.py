from __future__ import annotations

from typing import Any, Mapping, Type

from pydantic import BaseModel, Field
from layout_engine import AtomSpec


class AtomProps(BaseModel):
    """Loose schema for SwarmaKit atom props (override per framework atom)."""

    model_config = {"extra": "allow"}


class SwarmaAtom(BaseModel):
    """Typed wrapper around AtomSpec with prop/state helpers."""

    spec: AtomSpec
    props_schema: Type[AtomProps] = AtomProps
    state_defaults: Mapping[str, Any] = Field(default_factory=dict)

    def to_spec(self) -> AtomSpec:
        return self.spec

    def merge_props(self, overrides: Mapping[str, Any] | None = None) -> dict:
        merged = {**self.spec.defaults, **(overrides or {})}
        return self.props_schema(**merged).model_dump()

    def with_overrides(self, **patch: Any) -> "SwarmaAtom":
        """Return a copy with spec fields patched (e.g., new defaults/version)."""

        return self.model_copy(update={"spec": self.spec.with_overrides(**patch)})
