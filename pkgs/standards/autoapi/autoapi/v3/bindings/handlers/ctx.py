# autoapi/v3/bindings/handlers/ctx.py
from __future__ import annotations

from typing import Any, Mapping, Sequence


def _ctx_get(ctx: Mapping[str, Any], key: str, default: Any = None) -> Any:
    try:
        return ctx[key]
    except Exception:
        return getattr(ctx, key, default)


def _ctx_payload(ctx: Mapping[str, Any]) -> Any:
    v = _ctx_get(ctx, "payload", None)
    if isinstance(v, Mapping):
        return v
    if isinstance(v, Sequence) and not isinstance(v, (str, bytes)):
        return v
    return {}


def _ctx_db(ctx: Mapping[str, Any]) -> Any:
    return _ctx_get(ctx, "db")


def _ctx_request(ctx: Mapping[str, Any]) -> Any:
    return _ctx_get(ctx, "request")


def _ctx_path_params(ctx: Mapping[str, Any]) -> Mapping[str, Any]:
    v = _ctx_get(ctx, "path_params", None)
    return v if isinstance(v, Mapping) else {}


__all__ = [
    "_ctx_get",
    "_ctx_payload",
    "_ctx_db",
    "_ctx_request",
    "_ctx_path_params",
]
