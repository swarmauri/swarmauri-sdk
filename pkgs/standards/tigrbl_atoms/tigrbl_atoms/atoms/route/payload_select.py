from __future__ import annotations

from ...types import Atom, Ctx, BoundCtx
from ...stages import Bound

import json
from typing import Any, Mapping, Sequence

from ... import events as _ev
from ...opview import ensure_schema_in, opview_from_ctx

ANCHOR = _ev.ROUTE_PAYLOAD_SELECT


def _single_pk_name(model: type) -> str:
    table = getattr(model, "__table__", None)
    if table is None:
        raise ValueError(f"{model.__name__} has no __table__")
    pks = tuple(getattr(getattr(table, "primary_key", None), "columns", ()))
    if len(pks) != 1:
        raise NotImplementedError(
            f"{model.__name__} has composite PK; not supported by default core"
        )
    return pks[0].name


_BULKABLE_ALIASES = frozenset({"create", "update", "replace", "merge"})


def _is_valid_rpc_params(payload: Any) -> bool:
    if payload is None:
        return False
    if isinstance(payload, Mapping):
        return True
    return isinstance(payload, Sequence) and not isinstance(
        payload, (str, bytes, bytearray)
    )


def _set_invalid_rpc_params_error(temp: Any, payload: Any) -> None:
    if not isinstance(temp, dict):
        return
    temp["rpc_error"] = {
        "code": -32602,
        "message": "Invalid params",
        "data": {
            "reason": "JSON-RPC params must be an object or array.",
            "value_type": type(payload).__name__,
        },
    }


def _header_name_to_lookup(header_name: str) -> tuple[str, str]:
    raw = str(header_name)
    return raw, raw.lower()


def _merge_header_in_payload(ctx: Any, payload: Any) -> Any:
    if not isinstance(payload, Mapping):
        return payload

    temp = getattr(ctx, "temp", None)
    ingress = temp.get("ingress") if isinstance(temp, dict) else None
    headers = ingress.get("headers") if isinstance(ingress, dict) else None
    if not isinstance(headers, Mapping):
        return payload

    schema_in = temp.get("schema_in") if isinstance(temp, dict) else None
    if not isinstance(schema_in, Mapping):
        try:
            schema_in = ensure_schema_in(ctx, opview_from_ctx(ctx))
        except Exception:
            schema_in = None
    by_field = schema_in.get("by_field") if isinstance(schema_in, Mapping) else {}
    if not isinstance(by_field, Mapping):
        return payload

    merged = dict(payload)
    for field, meta in by_field.items():
        if not isinstance(meta, Mapping):
            continue
        header_name = meta.get("header_in")
        if not isinstance(header_name, str) or not header_name:
            continue
        exact, lowered = _header_name_to_lookup(header_name)
        value = headers.get(exact)
        if value is None:
            value = headers.get(lowered)
        if value is None:
            if bool(meta.get("header_required_in", False)) and field not in merged:
                merged[field] = None
            continue
        merged[field] = value
    return merged


def _coerce_route_params(ctx: Any, params: Mapping[str, Any]) -> dict[str, Any]:
    if not params:
        return {}

    model = getattr(ctx, "model", None)
    table = getattr(model, "__table__", None)
    columns = getattr(table, "columns", None)
    if columns is None:
        return dict(params)

    coerced: dict[str, Any] = {}
    for name, value in params.items():
        try:
            column = columns.get(name)
            py_type = getattr(getattr(column, "type", None), "python_type", None)
            if (
                py_type is not None
                and value is not None
                and not isinstance(value, py_type)
            ):
                coerced[name] = py_type(value)
                continue
        except Exception:
            pass
        coerced[name] = value
    return coerced


def _apply_route_params(payload: Any, params: Mapping[str, Any]) -> Any:
    if not params:
        return payload
    if isinstance(payload, Mapping):
        return {**dict(payload), **dict(params)}
    if isinstance(payload, Sequence) and not isinstance(
        payload, (str, bytes, bytearray)
    ):
        out: list[Any] = []
        for item in payload:
            if isinstance(item, Mapping):
                out.append({**dict(item), **dict(params)})
            else:
                out.append(item)
        return out
    return payload


def _promote_bulk_alias(ctx: Any, route: dict[str, Any], payload: Any) -> None:
    if not (
        isinstance(payload, Sequence)
        and not isinstance(payload, (str, bytes, bytearray, Mapping))
    ):
        return

    alias = route.get("op") or getattr(ctx, "op", None)
    if alias not in _BULKABLE_ALIASES:
        return

    bulk_alias = f"bulk_{alias}"
    plan = getattr(ctx, "kernel_plan", None) or getattr(ctx, "plan", None)
    opmeta = getattr(plan, "opmeta", ()) if plan is not None else ()
    model = route.get("model") or getattr(ctx, "model", None)

    for idx, meta in enumerate(opmeta):
        if (
            getattr(meta, "model", None) is model
            and getattr(meta, "alias", None) == bulk_alias
        ):
            route["op"] = bulk_alias
            route["opmeta_index"] = idx
            setattr(ctx, "op", bulk_alias)
            return


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)

    route = temp.setdefault("route", {})
    route_params_raw = (
        route.get("params") if isinstance(route.get("params"), Mapping) else {}
    )
    route_params = _coerce_route_params(ctx, route_params_raw)
    rpc_envelope = route.get("rpc_envelope")
    if isinstance(rpc_envelope, dict):
        payload = rpc_envelope.get("params", {})
        if not _is_valid_rpc_params(payload):
            _set_invalid_rpc_params_error(temp, payload)
            payload = {}
        if (
            isinstance(payload, Mapping)
            and set(payload.keys()) == {"params"}
            and isinstance(payload.get("params"), Mapping)
        ):
            payload = dict(payload["params"])
        rpc_method = rpc_envelope.get("method")
        if (
            isinstance(rpc_method, str)
            and rpc_method.endswith(".bulk_delete")
            and not isinstance(payload, dict)
        ):
            payload = {"ids": payload}
        payload = _apply_route_params(payload, route_params)
        if isinstance(payload, Mapping):
            try:
                pk_name = _single_pk_name(getattr(ctx, "model", None))
            except Exception:
                pk_name = None
            if pk_name and pk_name in payload:
                params = dict(route.get("params") or {})
                params.setdefault(pk_name, payload[pk_name])
                route["params"] = params
        route["payload"] = payload
        setattr(ctx, "payload", payload)
        return

    payload = route.get("payload")
    if payload is None:
        payload = getattr(ctx, "payload", None)
    if payload is None:
        ingress = temp.get("ingress") if isinstance(temp.get("ingress"), dict) else {}
        payload = ingress.get("body") if isinstance(ingress, dict) else None

    if isinstance(payload, (bytes, bytearray, memoryview)):
        try:
            payload = json.loads(bytes(payload).decode("utf-8"))
        except Exception:
            payload = {}

    if payload is not None:
        payload = _apply_route_params(payload, route_params)
        payload = _merge_header_in_payload(ctx, payload)
        _promote_bulk_alias(ctx, route, payload)
        route["payload"] = payload
        setattr(ctx, "payload", payload)


class AtomImpl(Atom[Bound, Bound]):
    name = "route.payload_select"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Bound]) -> Ctx[Bound]:
        _run(obj, ctx)
        return ctx.promote(BoundCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
