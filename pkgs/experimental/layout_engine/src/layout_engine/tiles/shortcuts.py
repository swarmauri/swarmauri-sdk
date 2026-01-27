from __future__ import annotations
from typing import Any
from .spec import TileSpec
from .default import Tile


def tile_spec(**kwargs) -> TileSpec:
    """Construct a :class:`TileSpec` (backward compatible helper)."""
    return TileSpec(**kwargs)


def define_tile(**kwargs) -> TileSpec:
    """Return a TileSpec from kwargs."""
    return TileSpec(**kwargs)


def derive_tile(base: TileSpec, **overrides: Any) -> TileSpec:
    """Immutable copy of a TileSpec with overrides."""
    data = base.__dict__.copy()
    data.update(overrides)
    return TileSpec(**data)


def make_tile(spec: TileSpec | None = None, **kwargs) -> Tile:
    """Return a Tile instance from a spec or kwargs."""
    if spec is None:
        spec = TileSpec(**kwargs)
    return Tile(spec=spec)
