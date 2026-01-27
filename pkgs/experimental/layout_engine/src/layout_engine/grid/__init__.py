"""Explicit grid model and resolver.

Public API:
- Data: GridTrack, GridSpec, GridTile
- Runtime: ExplicitGridResolver
- Utilities: tracks helpers, make_gridspec, place
- Bindings: to/from dict
"""

from .spec import GridTrack, GridSpec, GridTile
from .default import ExplicitGridResolver
from .shortcuts import (
    make_gridspec,
    place,
    tracks_fr,
    tracks_px,
    tracks_pct,
    make_gridspec_from_tokens,
    gridspec_from_tokens,
    breakpoint,
    breakpoints,
)
from .bindings import (
    gridspec_to_dict,
    gridspec_from_dict,
    gridtrack_to_dict,
    gridtrack_from_dict,
    gridtile_to_dict,
    gridtile_from_dict,
)

__all__ = [
    "GridTrack",
    "GridSpec",
    "GridTile",
    "ExplicitGridResolver",
    "make_gridspec",
    "place",
    "tracks_fr",
    "tracks_px",
    "tracks_pct",
    "make_gridspec_from_tokens",
    "gridspec_from_tokens",
    "breakpoint",
    "breakpoints",
    "gridspec_to_dict",
    "gridspec_from_dict",
    "gridtrack_to_dict",
    "gridtrack_from_dict",
    "gridtile_to_dict",
    "gridtile_from_dict",
]

from .default import Grid

__all__ = [*(globals().get("__all__", [])), "Grid"]

from .shortcuts import (
    define_gridspec as _define_gridspec,
    derive_gridspec as _derive_gridspec,
    make_grid as _make_grid,
)
from .decorators import with_breakpoints_ctx as _with_breakpoints_ctx

define_gridspec = _define_gridspec
derive_gridspec = _derive_gridspec
make_grid = _make_grid
with_breakpoints_ctx = _with_breakpoints_ctx

__all__ = list(
    set(
        [
            *(globals().get("__all__", [])),
            "define_gridspec",
            "derive_gridspec",
            "make_grid",
            "with_breakpoints_ctx",
        ]
    )
)
