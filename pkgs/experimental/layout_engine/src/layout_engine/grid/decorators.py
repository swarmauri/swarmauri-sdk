from __future__ import annotations
from functools import wraps
from typing import Iterable
from .spec import GridSpec, GridTrack
from ..core.size import Size, parse_size

def with_breakpoints_ctx(*breakpoints: tuple[int, list[str | float | int | Size | GridTrack]]):  # (max_w, columns)
    """Decorator to attach breakpoints to a GridSpec factory.

    Each breakpoint is a tuple: (max_width_px, columns), where `columns` is a list of
    - Size objects,
    - GridTrack(s), or
    - size expressions ('1fr', '200px', '33%') / numbers (px).

    Example:
        @with_breakpoints_ctx(
            (768,  ['1fr']),               # <=768px: single column
            (1280, ['1fr','1fr','1fr']),   # <=1280px: 3 cols
        )
        def build_spec() -> GridSpec:
            return make_gridspec([1,1,1,1])  # default (>=1280px): 4 cols
    """
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw) -> GridSpec:
            gs: GridSpec = fn(*a, **kw)
            bps: list[tuple[int, list[GridTrack]]] = []
            for max_w, cols in breakpoints:
                tracks: list[GridTrack] = []
                for c in cols:
                    if isinstance(c, GridTrack):
                        tracks.append(c)
                    elif isinstance(c, Size):
                        tracks.append(GridTrack(c))
                    elif isinstance(c, (int, float, str)):
                        s = parse_size(c)
                        tracks.append(GridTrack(s))
                    else:
                        raise TypeError(f"unsupported column descriptor: {type(c)}")
                bps.append((int(max_w), tracks))
            # attach (replace/extend) breakpoints
            gs.breakpoints = tuple(sorted(bps, key=lambda x: x[0]))  # type: ignore[attr-defined]
            return gs
        return wrapper
    return deco

def stable(fn):
    """No-op decorator placeholder to mark stable grid factories (policy hook)."""
    return fn
