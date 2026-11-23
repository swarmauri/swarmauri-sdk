from __future__ import annotations
from abc import ABC, abstractmethod
from ..core.viewport import Viewport
from ..core.frame import Frame
from .spec import GridSpec, GridTile


class IGridResolver(ABC):
    @abstractmethod
    def frames(
        self, spec: GridSpec, vp: Viewport, tiles: list[GridTile]
    ) -> dict[str, Frame]:
        """Compute absolute frames for tiles from a grid specification."""
        raise NotImplementedError
