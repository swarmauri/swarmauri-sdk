from __future__ import annotations
from typing import Mapping, Any, List, Tuple
from .spec import GridSpec, GridTrack, GridTile
from ..core.size import Size, parse_size

# ----------- GridTrack -----------
def gridtrack_to_dict(gt: GridTrack) -> dict:
    s = gt.size
    return {"size": {"value": s.value, "unit": s.unit, "min_px": s.min_px, "max_px": s.max_px}}

def gridtrack_from_dict(d: Mapping[str, Any]) -> GridTrack:
    s = d.get("size", {})
    size = Size(float(s.get("value", 0)), unit=s.get("unit", "px"), min_px=int(s.get("min_px", 0)), max_px=s.get("max_px"))
    return GridTrack(size)

# ----------- GridTile -----------
def gridtile_to_dict(gt: GridTile) -> dict:
    return {"tile_id": gt.tile_id, "col": gt.col, "row": gt.row, "col_span": gt.col_span, "row_span": gt.row_span}

def gridtile_from_dict(d: Mapping[str, Any]) -> GridTile:
    return GridTile(
        tile_id=str(d["tile_id"]),
        col=int(d["col"]), row=int(d["row"]),
        col_span=int(d.get("col_span", 1)),
        row_span=int(d.get("row_span", 1))
    )

# ----------- GridSpec -----------
def gridspec_to_dict(gs: GridSpec) -> dict:
    return {
        "row_height": gs.row_height,
        "gap_x": gs.gap_x,
        "gap_y": gs.gap_y,
        "columns": [gridtrack_to_dict(t) for t in gs.columns],
        "breakpoints": [
            (int(max_w), [gridtrack_to_dict(t) for t in tracks])
            for (max_w, tracks) in gs.breakpoints or []
        ],
    }

def gridspec_from_dict(d: Mapping[str, Any]) -> GridSpec:
    cols = [gridtrack_from_dict(x) for x in d.get("columns", [])]
    gs = GridSpec(columns=cols, row_height=int(d.get("row_height", 180)), gap_x=int(d.get("gap_x", 12)), gap_y=int(d.get("gap_y", 12)))
    bps: List[Tuple[int, list[GridTrack]]] = []
    for entry in d.get("breakpoints", []):
        max_w, cols_entry = entry
        tracks = [gridtrack_from_dict(t) for t in cols_entry]
        bps.append((int(max_w), tracks))
    if bps:
        gs.breakpoints = bps  # type: ignore[attr-defined]
    return gs
