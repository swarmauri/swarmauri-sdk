"""Compile package: explicit grid → frames, diffs, and view-model helpers."""

from .base import ILayoutCompiler
from .default import LayoutCompiler
from .utils import (
    frame_map_from_placements,
    frame_diff,
    frames_almost_equal,
    ordering_by_topleft,
    ordering_diff,
)

__all__ = [
    "ILayoutCompiler",
    "LayoutCompiler",
    "frame_map_from_placements",
    "frame_diff",
    "frames_almost_equal",
    "ordering_by_topleft",
    "ordering_diff",
]
