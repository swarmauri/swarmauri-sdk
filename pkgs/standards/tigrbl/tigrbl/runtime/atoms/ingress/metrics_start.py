from __future__ import annotations

from time import perf_counter
from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_METRICS_START


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    temp.setdefault("metrics", {}).setdefault("ingress_started_at", perf_counter())


__all__ = ["ANCHOR", "run"]
