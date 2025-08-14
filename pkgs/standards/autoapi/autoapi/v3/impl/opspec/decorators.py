# autoapi/v3/opspec/decorators.py
from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Iterable, Optional, Sequence, Tuple, Type

from .types import (
    OpSpec,
    PersistPolicy,
    TargetOp,
    Arity,
    ReturnForm,
    OpHook,  # for optional hook lists passed in
)

# ───────────────────────────────────────────────────────────────────────────────
# Class-level alias decorator
# ───────────────────────────────────────────────────────────────────────────────

def op_alias(
    *,
    alias: str,
    target: TargetOp,
    arity: Arity | None = None,
    persist: PersistPolicy = "default",
    request_model: Type | None = None,
    response_model: Type | None = None,
    http_methods: Sequence[str] | None = None,
    tags: Sequence[str] | None = None,
    rbac_guard_op: TargetOp | None = None,
    # optional extras
    path_suffix: str | None = None,
    returns: ReturnForm | None = None,
    hooks: Sequence[OpHook] | None = None,
    expose_routes: bool | None = None,
    expose_rpc: bool | None = None,
    expose_method: bool | None = None,
):
    """
    Declare an alias for a canonical target on a table class.

    Example:
        @op_alias(alias="soft_delete", target="delete", arity="member")
        class User(Base): ...
    """
    def deco(table_cls: Type):
        # attach to __autoapi_ops__ without touching the imperative registry
        ops = list(getattr(table_cls, "__autoapi_ops__", ()))
        spec = OpSpec(
            alias=alias,
            target=target,
            table=table_cls,
            arity=arity or ("member" if target in {"read","update","replace","delete"} else "collection"),
            persist=persist,
            request_model=request_model,
            response_model=response_model,
            http_methods=tuple(http_methods) if http_methods else None,
            path_suffix=path_suffix,
            tags=tuple(tags) if tags else (),
            rbac_guard_op=rbac_guard_op,
            returns=returns or ("model" if target != "clear" else "raw"),
            hooks=tuple(hooks) if hooks else (),
            # exposure toggles (fall back to OpSpec defaults when None)
            expose_routes=True if expose_routes is None else bool(expose_routes),
            expose_rpc=True if expose_rpc is None else bool(expose_rpc),
            expose_method=True if expose_method is None else bool(expose_method),
        )
        ops.append(spec)
        setattr(table_cls, "__autoapi_ops__", tuple(ops))
        return table_cls
    return deco


# ───────────────────────────────────────────────────────────────────────────────
# Function/method-level custom op decorator
# ───────────────────────────────────────────────────────────────────────────────

def custom_op(
    *,
    alias: str,
    arity: Arity = "collection",
    persist: PersistPolicy = "default",
    returns: ReturnForm = "model",
    request_model: Type | None = None,
    response_model: Type | None = None,
    http_methods: Sequence[str] | None = None,
    tags: Sequence[str] | None = None,
    rbac_guard_op: TargetOp | None = None,
    path_suffix: str | None = None,
    hooks: Sequence[OpHook] | None = None,
    expose_routes: bool | None = None,
    expose_rpc: bool | None = None,
    expose_method: bool | None = None,
):
    """
    Mark a method/function as a custom operation. The collector will:
      • set `table` to the owning class,
      • use the decorated function as the raw handler if the stored spec's
        `handler` is None,
      • merge into the model’s OpSpec set with high precedence.

    Example:
        class Wheel(Base):
            @custom_op(alias="rotate", arity="member", persist="override", returns="raw")
            async def rotate(self, *, ctx, db, request, payload):
                ...
    """
    def deco(fn: Callable[..., Any]):
        @wraps(fn)
        def _raw(*a, **kw):
            # executor can await return values; keep wrapper sync-friendly
            return fn(*a, **kw)

        # Stash an OpSpec shell; binder/collector will set table and handler.
        _raw.__autoapi_custom_op__ = OpSpec(  # type: ignore[attr-defined]
            alias=alias,
            target="custom",
            table=None,
            arity=arity,
            persist=persist,
            returns=returns,
            handler=None,  # collector will set to the decorated function if still None
            request_model=request_model,
            response_model=response_model,
            http_methods=tuple(http_methods) if http_methods else None,
            path_suffix=path_suffix,
            tags=tuple(tags) if tags else (),
            rbac_guard_op=rbac_guard_op,
            hooks=tuple(hooks) if hooks else (),
            expose_routes=True if expose_routes is None else bool(expose_routes),
            expose_rpc=True if expose_rpc is None else bool(expose_rpc),
            expose_method=True if expose_method is None else bool(expose_method),
        )
        return _raw
    return deco


__all__ = ["op_alias", "custom_op"]
