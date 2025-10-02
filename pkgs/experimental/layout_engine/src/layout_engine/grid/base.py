from __future__ import annotations
from typing import Protocol
from ..core.viewport import Viewport
from ..core.frame import Frame
from .spec import GridSpec, GridTile

class IGridResolver(Protocol):
    def frames(self, spec: GridSpec, vp: Viewport, tiles: list[GridTile]) -> dict[str, Frame]: ...
