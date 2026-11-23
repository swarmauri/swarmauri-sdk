from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Mapping, Any
from .spec import TileSpec


class ITile(ABC):
    """Runtime tile object (thin wrapper around TileSpec)."""

    @property
    @property
    @abstractmethod
    def spec(self) -> TileSpec:
        """Bound TileSpec for this runtime Tile."""
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> Mapping[str, Any]:
        """Serialize tile to a JSON-safe dict."""
        raise NotImplementedError


class ITileFactory(ABC):
    @abstractmethod
    def __call__(self, **kwargs) -> ITile:
        """Create a tile from keyword arguments/builder context."""
        raise NotImplementedError
