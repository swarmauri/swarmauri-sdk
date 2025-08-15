from __future__ import annotations
from functools import wraps
from typing import Any, Callable, Sequence, Type
from .spec import OpSpec, PersistPolicy, TargetOp, Arity, ReturnForm


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
):
    def deco(table_cls: Type):
        # attach to __autoapi_ops__ without forcing import-time registry
        ops = list(getattr(table_cls, "__autoapi_ops__", ()))
        ops.append(
            OpSpec(
                alias=alias,
                target=target,
                table=table_cls,
                arity=arity,
                persist=persist,
                request_model=request_model,
                response_model=response_model,
                http_methods=http_methods,
                tags=tags,
                rbac_guard_op=rbac_guard_op,
            )
        )
        table_cls.__autoapi_ops__ = tuple(ops)
        return table_cls

    return deco


def custom_op(
    *,
    alias: str,
    arity: Arity,
    persist: PersistPolicy = "override",
    returns: ReturnForm = "model",
    request_model: Type | None = None,
    response_model: Type | None = None,
    http_methods: Sequence[str] | None = ("POST",),
    tags: Sequence[str] | None = None,
    rbac_guard_op: TargetOp | None = None,
):
    def deco(fn: Callable[..., Any]):
        @wraps(fn)
        async def wrapper(*a, **kw):
            return await fn(*a, **kw)

        # stash an OpSpec shell; table gets filled at class bind
        wrapper.__autoapi_custom_op__ = OpSpec(
            alias=alias,
            target="custom",
            table=None,
            arity=arity,
            persist=persist,
            returns=returns,
            handler=None,
            request_model=request_model,
            response_model=response_model,
            http_methods=http_methods,
            tags=tags,
            rbac_guard_op=rbac_guard_op,
        )
        return wrapper

    return deco
