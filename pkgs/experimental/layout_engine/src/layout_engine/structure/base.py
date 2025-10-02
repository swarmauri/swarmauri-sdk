from __future__ import annotations
from typing import Protocol
from ..core.viewport import Viewport
from ..grid.spec import GridSpec, GridTile
from .spec import Table

class IGridBuilder(Protocol):
    """Convert an authoring Table into an explicit GridSpec and placements."""
    def to_grid(self, t: Table, vp: Viewport) -> tuple[GridSpec, list[GridTile]]: ...
