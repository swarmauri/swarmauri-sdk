from __future__ import annotations

from urllib.parse import parse_qs
from typing import Any, MutableMapping

from ... import events as _ev

ANCHOR = _ev.INGRESS_QUERY_PARSE


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def run(obj: object | None, ctx: Any) -> None:
    del obj
    parsed: dict[str, Any] | None = None

    request = getattr(ctx, "request", None)
    query = getattr(request, "query_params", None) if request is not None else None
    if query is not None:
        parsed = dict(query)

    if parsed is None:
        gw_raw = getattr(ctx, "gw_raw", None)
        gw_query = getattr(gw_raw, "query", None) if gw_raw is not None else None
        if gw_query is not None:
            parsed = dict(gw_query)

    if parsed is None:
        raw = getattr(ctx, "raw", None)
        scope = getattr(raw, "scope", None) if raw is not None else None
        if isinstance(scope, dict):
            query_string = scope.get("query_string", b"")
            if isinstance(query_string, (bytes, bytearray)):
                parsed = parse_qs(
                    bytes(query_string).decode("latin-1"), keep_blank_values=True
                )
            elif isinstance(query_string, str):
                parsed = parse_qs(query_string, keep_blank_values=True)

    if parsed is None:
        return

    temp = _ensure_temp(ctx)
    temp.setdefault("ingress", {})["query"] = parsed
    setattr(ctx, "query", parsed)


__all__ = ["ANCHOR", "run"]
