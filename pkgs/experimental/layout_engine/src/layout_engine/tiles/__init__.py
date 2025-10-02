"""Tiles: atomic layout units with semantic roles and constraints.

Exports
-------
- TileSpec: immutable spec with constraints, role, and props/meta
- ITile: protocol for runtime tile objects
- Tile: default ITile implementation
- Shortcuts: tile_spec(), make_tile(), define_tile(), derive_tile()
- Bindings: to_dict()/from_dict() (spec), tile_to_dict()/tile_from_dict()
- Decorators: @tile(...), @validate_spec
"""
from .spec import TileSpec, validate_tile_id, validate_role
from .base import ITile, ITileFactory
from .default import Tile
from .shortcuts import tile_spec, make_tile, define_tile, derive_tile
from .decorators import tile, validate_spec
from .bindings import to_dict, from_dict, tile_to_dict, tile_from_dict

__all__ = [
    "TileSpec","validate_tile_id","validate_role",
    "ITile","ITileFactory","Tile",
    "tile_spec","make_tile","define_tile","derive_tile",
    "tile","validate_spec",
    "to_dict","from_dict","tile_to_dict","tile_from_dict",
]
