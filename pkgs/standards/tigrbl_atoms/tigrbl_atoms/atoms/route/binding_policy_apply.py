from __future__ import annotations

from ...types import Atom, Ctx, BoundCtx
from ...stages import Bound

from typing import Any, Mapping

from ... import events as _ev

ANCHOR = _ev.ROUTE_BINDING_POLICY_APPLY


def _collect_header_overrides(model: Any, alias: str) -> list[tuple[str, str, bool]]:
    fields: list[tuple[str, str, bool]] = []
    for field, spec in (getattr(model, "__tigrbl_cols__", {}) or {}).items():
        io = getattr(spec, "io", None)
        header_in = getattr(io, "header_in", None) if io is not None else None
        if not isinstance(header_in, str) or not header_in:
            continue

        in_verbs = set(getattr(io, "in_verbs", ()) or ())
        if alias not in in_verbs:
            continue
        fields.append(
            (field, header_in.lower(), bool(getattr(io, "header_required_in", False)))
        )
    return fields


def _headers_from_ctx(ctx: Any) -> dict[str, Any]:
    headers = getattr(ctx, "headers", None)
    if isinstance(headers, Mapping):
        return {str(k).lower(): v for k, v in headers.items()}

    temp = getattr(ctx, "temp", None)
    ingress = temp.get("ingress") if isinstance(temp, dict) else None
    raw = ingress.get("headers") if isinstance(ingress, Mapping) else None
    if isinstance(raw, Mapping):
        return {str(k).lower(): v for k, v in raw.items()}

    return {}


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})
    if "policy" not in route:
        route["policy"] = getattr(ctx, "binding_policy", None)

    payload = route.get("payload")
    if not isinstance(payload, Mapping):
        return

    model = route.get("model") or getattr(ctx, "model", None)
    alias = route.get("op") or getattr(ctx, "op", None)
    if model is None or not isinstance(alias, str):
        return

    header_fields = _collect_header_overrides(model, alias)
    if not header_fields:
        return

    headers = _headers_from_ctx(ctx)
    merged = dict(payload)

    for field, header_name, required in header_fields:
        value = headers.get(header_name)
        if value is None:
            if required:
                merged.pop(field, None)
            continue
        if isinstance(value, list):
            value = value[-1] if value else None
        if value is not None:
            merged[field] = value

    route["payload"] = merged
    setattr(ctx, "payload", merged)


class AtomImpl(Atom[Bound, Bound]):
    name = "route.binding_policy_apply"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Bound]) -> Ctx[Bound]:
        _run(obj, ctx)
        return ctx.promote(BoundCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
