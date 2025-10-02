from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Optional
from enum import Enum

Unit = Literal["px","fr","%"]

class SizeToken(str, Enum):
    xxs = "xxs"; xs = "xs"; s = "s"; m = "m"; l = "l"; xl = "xl"; xxl = "xxl"

DEFAULT_TOKEN_WEIGHTS: dict[SizeToken, float] = {
    SizeToken.xxs: 0.5,
    SizeToken.xs:  0.75,
    SizeToken.s:   1.0,
    SizeToken.m:   1.5,
    SizeToken.l:   2.0,
    SizeToken.xl:  3.0,
    SizeToken.xxl: 4.0,
}

@dataclass(frozen=True)
class Size:
    value: float
    unit: Unit = "px"
    min_px: int = 0
    max_px: Optional[int] = None
