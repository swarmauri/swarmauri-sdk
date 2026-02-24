# tigrbl/v3/bindings/handlers/ctx.py
from __future__ import annotations
import logging

from typing import Any, Mapping, Sequence

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/handlers/ctx")


def _ctx_get(ctx: Mapping[str, Any], key: str, default: Any = None) -> Any:
    logger.debug("_ctx_get retrieving key '%s'", key)
    try:
        value = ctx[key]
        logger.debug("Key '%s' found via mapping access", key)
        return value
    except Exception:
        logger.debug("Key '%s' not found; using getattr fallback", key)
        return getattr(ctx, key, default)


def _ctx_payload(ctx: Mapping[str, Any]) -> Any:
    temp = _ctx_get(ctx, "temp", None)
    raw = _ctx_get(ctx, "payload", None)
    if isinstance(temp, Mapping):
        av = temp.get("assembled_values")
        if isinstance(av, Mapping) and isinstance(raw, Mapping):
            merged = dict(raw)
            merged.update(av)
            logger.debug("Payload from assembled values: %s", merged)
            return merged

    v = raw
    if isinstance(v, Mapping):
        logger.debug("Payload is a mapping")
        logger.debug("Payload: %s", v)
        return v
    if isinstance(v, Sequence) and not isinstance(v, (str, bytes)):
        logger.debug("Payload is a non-string sequence")
        logger.debug("Payload: %s", v)
        return v
    logger.debug("Payload absent or unsupported; defaulting to empty dict")
    v = {}
    logger.debug("Payload: %s", v)
    return v


def _ctx_db(ctx: Mapping[str, Any]) -> Any:
    logger.debug("Retrieving 'db' from context")
    return _ctx_get(ctx, "db")


def _ctx_request(ctx: Mapping[str, Any]) -> Any:
    logger.debug("Retrieving 'request' from context")
    return _ctx_get(ctx, "request")


def _ctx_path_params(ctx: Mapping[str, Any]) -> Mapping[str, Any]:
    v = _ctx_get(ctx, "path_params", None)
    if isinstance(v, Mapping):
        logger.debug("Path params found: %s", list(v.keys()))
        return v
    logger.debug("No path params found; returning empty mapping")
    return {}


__all__ = [
    "_ctx_get",
    "_ctx_payload",
    "_ctx_db",
    "_ctx_request",
    "_ctx_path_params",
]
