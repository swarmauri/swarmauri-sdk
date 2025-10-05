from __future__ import annotations
from abc import ABC, abstractmethod
from ..core.viewport import Viewport
from ..core.frame import Frame
from ..grid.spec import GridSpec, GridTile

class ILayoutCompiler(ABC):
    """Contract for turning explicit grids into pixel frames.

    Minimal required method keeps the engine decoupled from authoring and manifests.
    """
    @abstractmethod
    def frames(self, gs: GridSpec, vp: Viewport, placements: list[GridTile]) -> dict[str, Frame]:
        raise NotImplementedError
