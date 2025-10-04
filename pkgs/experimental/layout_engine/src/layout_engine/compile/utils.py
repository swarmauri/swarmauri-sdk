from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Literal
from ..core.frame import Frame
from ..grid.spec import GridSpec, GridTile
from ..tiles.spec import TileSpec
from ..core.viewport import Viewport
from ..grid.base import IGridResolver
from ..grid.default import ExplicitGridResolver

def frame_map_from_placements(gs: GridSpec, vp: Viewport, placements: list[GridTile], resolver: IGridResolver | None = None) -> dict[str, Frame]:
    """Convenience: compute frames map for given placements with optional resolver injection."""
    r = resolver or ExplicitGridResolver()
    return r.frames(gs, vp, placements)

@dataclass(frozen=True)

def frames_almost_equal(a: Frame, b: Frame, epsilon: int = 0) -> bool:
    return (
        abs(a.x - b.x) <= epsilon and
        abs(a.y - b.y) <= epsilon and
        abs(a.w - b.w) <= epsilon and
        abs(a.h - b.h) <= epsilon
    )


def frame_diff(old: dict[str, Frame], new: dict[str, Frame], *, epsilon: int = 0) -> dict:
    """Compute a diff between two frame maps.

    Returns a dict with:
      - added:   [tile_id]
      - removed: [tile_id]
      - changed: [tile_id]
      - unchanged: [tile_id]
      - changes: [FrameChange]
    """
    old_keys = set(old.keys())
    new_keys = set(new.keys())
    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)

    changed: list[str] = []
    unchanged: list[str] = []
    changes: list[FrameChange] = []

    for tid in sorted(old_keys & new_keys):
        a = old[tid]; b = new[tid]
        if frames_almost_equal(a, b, epsilon=epsilon):
            unchanged.append(tid)
            changes.append(FrameChange(tile_id=tid, before=a, after=b, kind="unchanged"))
        else:
            changed.append(tid)
            changes.append(FrameChange(tile_id=tid, before=a, after=b, kind="changed"))

    for tid in added:
        changes.append(FrameChange(tile_id=tid, before=None, after=new[tid], kind="added"))
    for tid in removed:
        changes.append(FrameChange(tile_id=tid, before=old[tid], after=None, kind="removed"))

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
        "changes": changes,
    }


def ordering_by_topleft(frames_map: dict[str, Frame]) -> list[str]:
    """Return tile ids sorted by (y, x, id) to provide a stable, visual ordering."""
    return sorted(frames_map.keys(), key=lambda k: (frames_map[k].y, frames_map[k].x, k))


def ordering_diff(before_ids: list[str], after_ids: list[str]) -> list[tuple[str, int, int]]:
    """Compute simple positional index moves between two orderings.

    Returns a list of (tile_id, old_index, new_index) for ids present in both lists where index changed.
    """
    before_pos = {tid: i for i, tid in enumerate(before_ids)}
    moves: list[tuple[str,int,int]] = []
    for j, tid in enumerate(after_ids):
        if tid in before_pos:
            i = before_pos[tid]
            if i != j:
                moves.append((tid, i, j))
    return moves
