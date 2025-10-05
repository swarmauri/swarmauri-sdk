from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Frame:
    x: int; y: int; w: int; h: int
