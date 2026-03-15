from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from .serde import SerdeMixin


@dataclass(slots=True)
class TableRegistrySpec(SerdeMixin):
    """Spec payload for building a table registry."""

    tables: Sequence[Any] = field(default_factory=tuple)


__all__ = ["TableRegistrySpec"]
