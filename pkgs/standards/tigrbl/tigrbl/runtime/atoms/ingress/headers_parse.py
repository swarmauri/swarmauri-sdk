from __future__ import annotations

from collections import defaultdict
from typing import Any

from ... import events as _ev

ANCHOR = _ev.INGRESS_HEADERS_PARSE


def _parse_raw_headers(scope: dict[str, Any]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    raw_headers = scope.get("headers")
    if not isinstance(raw_headers, list):
        return {}

    for item in raw_headers:
        if (
            isinstance(item, tuple)
            and len(item) == 2
            and isinstance(item[0], (bytes, bytearray))
            and isinstance(item[1], (bytes, bytearray))
        ):
            key = bytes(item[0]).decode("latin-1").lower()
            value = bytes(item[1]).decode("latin-1")
            out[key].append(value)
    return dict(out)


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)

    request = getattr(ctx, "request", None)
    headers = getattr(request, "headers", None) if request is not None else None

    parsed: dict[str, Any] | None = None
    if headers is not None:
        parsed = dict(headers)

    if parsed is None:
        raw = getattr(ctx, "raw", None)
        scope = getattr(raw, "scope", None) if raw is not None else None
        if isinstance(scope, dict):
            parsed = _parse_raw_headers(scope)

    if parsed is not None:
        temp.setdefault("ingress", {})["headers"] = parsed
        setattr(ctx, "headers", parsed)


__all__ = ["ANCHOR", "run"]
