from __future__ import annotations

from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict, Field
from layout_engine import AtomSpec


class AtomPreset(BaseModel):
    """Declarative definition of a UI atom preset.

    Presets extend :class:`layout_engine.AtomSpec` with optional metadata that lets
    downstream packages reason about origin, families, or display names.
    """

    model_config = ConfigDict(frozen=True)

    role: str
    module: str
    export: str = "default"
    version: str = "1.0.0"
    defaults: Mapping[str, Any] = Field(default_factory=dict)
    family: str | None = None
    description: str | None = None

    def to_spec(self) -> AtomSpec:
        """Convert the preset into a concrete :class:`AtomSpec`."""
        return AtomSpec(
            role=self.role,
            module=self.module,
            export=self.export,
            version=self.version,
            defaults=dict(self.defaults),
        )
