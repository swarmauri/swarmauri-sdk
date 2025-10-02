from __future__ import annotations
from typing import Protocol
from ..core.viewport import Viewport
from ..core.frame import Frame
from ..grid.spec import GridSpec, GridTile

class ILayoutCompiler(Protocol):
    """Contract for turning explicit grids into pixel frames.

    Minimal required method keeps the engine decoupled from authoring and manifests.
    """
    def frames(self, gs: GridSpec, vp: Viewport, placements: list[GridTile]) -> dict[str, Frame]: ...
