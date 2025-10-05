from __future__ import annotations
from abc import ABC, abstractmethod
from ..core.viewport import Viewport
from ..grid.spec import GridSpec, GridTile
from .spec import Table

class IGridBuilder(ABC):
    """Convert an authoring Table into an explicit GridSpec and placements."""
    def to_grid(self, t: Table, vp: Viewport) -> tuple[GridSpec, list[GridTile]]: ...
