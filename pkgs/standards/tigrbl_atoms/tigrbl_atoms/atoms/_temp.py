from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Sequence


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def _record_hydration(
    ctx: Any,
    values: Mapping[str, Any],
    *,
    via_returning: bool = False,
    replace: bool = False,
) -> None:
    """Record DB hydration values and optional RETURNING provenance."""
    temp = _ensure_temp(ctx)
    if via_returning:
        temp["used_returning"] = True
    if not isinstance(values, Mapping):
        return

    hydrated = temp.get("hydrated_values")
    if replace or not isinstance(hydrated, dict):
        temp["hydrated_values"] = dict(values)
        return
    hydrated.update(values)


def _ensure_response_extras(ctx: Any) -> MutableMapping[str, Any]:
    """Return a mutable extras buffer stored in ``ctx.temp['response_extras']``."""
    temp = _ensure_temp(ctx)
    buffer = temp.get("response_extras")
    if not isinstance(buffer, dict):
        buffer = {}
        temp["response_extras"] = buffer
    return buffer


def _add_response_extras(
    ctx: Any,
    extras: Mapping[str, Any],
    *,
    overwrite: bool = False,
) -> Sequence[str]:
    """Merge extras into ``ctx.temp['response_extras']`` and return skipped keys."""
    if not isinstance(extras, Mapping) or not extras:
        return ()

    buffer = _ensure_response_extras(ctx)

    conflicts: list[str] = []
    for key, value in extras.items():
        if (key in buffer) and not overwrite:
            conflicts.append(key)
            continue
        buffer[key] = value
    return tuple(conflicts)


def _response_payload(ctx: Any) -> Any:
    """Return the canonical response payload stored on context."""
    payload = getattr(ctx, "response_payload", None)
    if payload is not None:
        return payload
    temp = getattr(ctx, "temp", None)
    if isinstance(temp, Mapping):
        return temp.get("response_payload")
    return None


def _set_response_payload(ctx: Any, payload: Any) -> None:
    """Set response payload on context and mirror to temp for compatibility."""
    setattr(ctx, "response_payload", payload)
    temp = _ensure_temp(ctx)
    temp["response_payload"] = payload


__all__ = [
    "_ensure_temp",
    "_record_hydration",
    "_ensure_response_extras",
    "_add_response_extras",
    "_response_payload",
    "_set_response_payload",
]
