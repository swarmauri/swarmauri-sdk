from __future__ import annotations
from typing import Protocol, Mapping, Any
from .spec import TileSpec

class ITile(Protocol):
    """Runtime tile object (thin wrapper around TileSpec)."""
    @property
    def spec(self) -> TileSpec: ...
    def to_dict(self) -> Mapping[str, Any]: ...

class ITileFactory(Protocol):
    def __call__(self, **kwargs) -> ITile: ...
