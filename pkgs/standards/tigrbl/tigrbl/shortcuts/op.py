from __future__ import annotations

from typing import Any


def make(**kwargs: Any):
    from tigrbl import Op

    return Op(**kwargs)


op = make

__all__ = ["make", "op"]
