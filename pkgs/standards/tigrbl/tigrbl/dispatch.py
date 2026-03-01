from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict


def _resolve_model(router: Any | None, model_or_name: type | str) -> type:
    if isinstance(model_or_name, type):
        return model_or_name

    tables = getattr(router, "tables", {}) if router is not None else {}
    model = tables.get(model_or_name) if hasattr(tables, "get") else None
    if model is None:
        raise AttributeError(f"Unknown model '{model_or_name}'")
    return model


def resolve_operation(
    *, router: Any | None, model_or_name: type | str, alias: str
) -> SimpleNamespace:
    model = _resolve_model(router, model_or_name)

    # Import lazily to avoid bootstrap cycles.
    from .mapping.op_resolver import resolve as resolve_ops

    specs = resolve_ops(model)
    spec = next((sp for sp in specs if sp.alias == alias), None)
    target = spec.target if spec is not None else alias
    return SimpleNamespace(model=model, target=target, alias=alias)


async def dispatch_operation(
    *,
    router: Any | None = None,
    model_or_name: type | str,
    alias: str,
    payload: Any = None,
    db: Any | None = None,
    request: Any = None,
    ctx: Dict[str, Any] | None = None,
    seed_ctx: Dict[str, Any] | None = None,
    target: str | None = None,
    rpc_mode: bool = True,
    response_serializer: Any | None = None,
) -> Any:
    del target, rpc_mode

    resolution = resolve_operation(router=router, model_or_name=model_or_name, alias=alias)
    model = resolution.model
    fn = getattr(getattr(model, "rpc", SimpleNamespace()), alias, None)
    if fn is None:
        raise AttributeError(f"{getattr(model, '__name__', model)} has no RPC method '{alias}'")

    merged_ctx: Dict[str, Any] = {}
    if seed_ctx:
        merged_ctx.update(seed_ctx)
    if ctx:
        merged_ctx.update(ctx)

    result = await fn(payload, db=db, request=request, ctx=merged_ctx)
    if response_serializer is not None:
        return response_serializer(result)
    return result


__all__ = ["dispatch_operation", "resolve_operation"]
