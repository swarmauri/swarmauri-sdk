from __future__ import annotations

import inspect
from typing import Any

from pydantic import BaseModel

from ... import events as _ev
from ....mapping import engine_resolver as _resolver

ANCHOR = _ev.ROUTE_CTX_FINALIZE
_METADATA_OP_ALIASES = {"__openapi__", "__docs__"}
_RUNTIME_ROUTE_ALIAS_PREFIX = "__route__:"


def _requires_db(model: type, alias: str) -> bool:
    opspecs = getattr(getattr(model, "opspecs", None), "all", ()) or ()
    for spec in opspecs:
        if getattr(spec, "alias", None) != alias:
            continue
        return getattr(spec, "persist", "default") != "skip"
    return True


def _select_out_model(model: type, alias: str):
    schemas_root = getattr(model, "schemas", None)
    alias_ns = getattr(schemas_root, alias, None) if schemas_root else None
    if not alias_ns:
        return None

    target = alias.split(".")[-1]
    if target in {"bulk_create", "bulk_update", "bulk_replace", "bulk_merge"}:
        return getattr(alias_ns, "out_item", None)
    return getattr(alias_ns, "out", None)


def _build_response_serializer(model: type, alias: str):
    if alias.split(".")[-1] in {"delete", "bulk_delete", "clear"}:
        return None

    out_model = _select_out_model(model, alias)
    if (
        not out_model
        or not inspect.isclass(out_model)
        or not issubclass(out_model, BaseModel)
    ):
        return None

    def _serialize(value: Any) -> Any:
        if isinstance(value, (list, tuple)):
            return [
                out_model.model_validate(item).model_dump(
                    exclude_none=False, by_alias=True
                )
                for item in value
            ]
        return out_model.model_validate(value).model_dump(
            exclude_none=False, by_alias=True
        )

    return _serialize


def run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    route = temp.setdefault("route", {})
    route["finalized"] = True

    if getattr(ctx, "db", None) is not None:
        return

    model = getattr(ctx, "model", None)
    op_alias = getattr(ctx, "op", None)
    router = getattr(ctx, "router", None) or getattr(ctx, "app", None)
    if model is None or op_alias is None:
        return

    serializer = _build_response_serializer(model, op_alias)
    if callable(serializer):
        setattr(ctx, "response_serializer", serializer)

    if op_alias in _METADATA_OP_ALIASES or str(op_alias).startswith(
        _RUNTIME_ROUTE_ALIAS_PREFIX
    ):
        return

    if not _requires_db(model, op_alias):
        return

    try:
        db, release = _resolver.acquire(router=router, model=model, op_alias=op_alias)
    except RuntimeError:
        model_get_db = getattr(model, "__tigrbl_get_db__", None)
        router_get_db = getattr(router, "get_db", None)
        get_db = model_get_db if callable(model_get_db) else router_get_db
        if not callable(get_db):
            raise
        db = get_db()

        def release() -> None:
            close = getattr(db, "close", None)
            if callable(close):
                close()

    setattr(ctx, "db", db)
    temp["__sys_db_release__"] = release


__all__ = ["ANCHOR", "run"]
