from __future__ import annotations
from typing import Mapping, Any
from .default import Tile
from .spec import TileSpec

def tile_spec(**kwargs) -> TileSpec:
    """Create a TileSpec with validation."""
    return TileSpec(**kwargs)

def make_tile(**kwargs) -> Tile:
    """Convenience factory for Tile(TileSpec(**kwargs))."""
    return Tile(TileSpec(**kwargs))

def define_tile(spec: TileSpec) -> Tile:
    """Wrap an existing TileSpec in a Tile object."""
    return Tile(spec)

def derive_tile(base: TileSpec, **overrides: Any) -> TileSpec:
    """Immutable copy with overrides."""
    return base.with_overrides(**overrides)
