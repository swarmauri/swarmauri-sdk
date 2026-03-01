from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass
class TableRegistrySpec:
    """Spec payload for building a table registry."""

    tables: Sequence[Any] = field(default_factory=tuple)


__all__ = ["TableRegistrySpec"]
