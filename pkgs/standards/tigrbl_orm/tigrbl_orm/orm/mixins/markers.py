from __future__ import annotations

from tigrbl.types import declarative_mixin


@declarative_mixin
class AsyncCapable:
    pass


@declarative_mixin
class Audited:
    pass


__all__ = ["AsyncCapable", "Audited"]
