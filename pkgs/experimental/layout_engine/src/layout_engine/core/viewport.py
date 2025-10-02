from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Viewport:
    width: int
    height: int
