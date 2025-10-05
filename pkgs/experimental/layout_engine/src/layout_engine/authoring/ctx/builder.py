from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List

@dataclass
class ColCtx:
    size: str
    items: List[Any] = field(default_factory=list)
    def __enter__(self): return self
    def __exit__(self, *exc): return False
    def add(self, *components: Any) -> "ColCtx":
        self.items.extend(components)
        return self

@dataclass
class RowCtx:
    height_rows: int = 1
    cols: List[ColCtx] = field(default_factory=list)
    def __enter__(self): return self
    def __exit__(self, *exc): return False
    def col(self, size: str) -> ColCtx:
        c = ColCtx(size=size); self.cols.append(c); return c

@dataclass
class TableCtx:
    rows: List[RowCtx] = field(default_factory=list)
    gap_x: int = 12
    gap_y: int = 12
    def __enter__(self): return self
    def __exit__(self, *exc): return False
    def row(self, *, height_rows: int = 1) -> RowCtx:
        r = RowCtx(height_rows=height_rows); self.rows.append(r); return r
