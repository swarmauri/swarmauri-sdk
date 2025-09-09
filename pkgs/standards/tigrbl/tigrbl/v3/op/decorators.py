"""Operation-related decorators for Tigrbl v3."""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional, Sequence, Union

from .types import OpSpec, Arity, TargetOp, PersistPolicy
from ..schema.types import SchemaArg


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _unwrap(obj: Any) -> Callable[..., Any]:
    """Get underlying function for (class|static)method; else return obj."""
    if isinstance(obj, (classmethod, staticmethod)):
        return obj.__func__  # type: ignore[attr-defined]
    return obj


def _ensure_cm(func: Any) -> Any:
    """Ensure method is a classmethod so it receives (cls, ctx)."""
    if isinstance(func, (classmethod, staticmethod)):
        return func
    return classmethod(func)


def _maybe_await(v):
    if inspect.isawaitable(v):
        return v

    async def _done():
        return v

    return _done()


# ---------------------------------------------------------------------------
# alias_ctx with optional rich overrides
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AliasDecl:
    alias: str
    # Optional overrides (lazy-capable schema args are fine; resolved later)
    request_schema: Optional[SchemaArg] = None
    response_schema: Optional[SchemaArg] = None
    persist: Optional[PersistPolicy] = None
    arity: Optional[Arity] = None
    rest: Optional[bool] = None


def alias(name: str, **kw) -> AliasDecl:
    """Convenience helper: alias('get', response_schema=..., rest=False)."""
    return AliasDecl(alias=name, **kw)


def alias_ctx(**verb_to_alias_or_decl: Union[str, AliasDecl]):
    """Class decorator mapping canonical verbs → aliases with optional overrides."""

    def deco(cls: type):
        amap = dict(getattr(cls, "__tigrbl_aliases__", {}) or {})
        overrides = dict(getattr(cls, "__tigrbl_alias_overrides__", {}) or {})

        for canon, value in verb_to_alias_or_decl.items():
            if isinstance(value, AliasDecl):
                amap[canon] = value.alias
                overrides[canon] = {
                    "request_schema": value.request_schema,
                    "response_schema": value.response_schema,
                    "persist": value.persist,
                    "arity": value.arity,
                    "rest": value.rest,
                }
            elif isinstance(value, str):
                amap[canon] = value
            else:
                raise TypeError(
                    f"alias_ctx[{canon}] must be str or AliasDecl, got {type(value)}"
                )

        setattr(cls, "__tigrbl_aliases__", amap)
        setattr(cls, "__tigrbl_alias_overrides__", overrides)
        try:  # clear cached alias maps so late-applied decorators take effect
            from .mro_collect import mro_alias_map_for

            mro_alias_map_for.cache_clear()
        except Exception:  # pragma: no cover - best effort
            pass
        return cls

    return deco


# ---------------------------------------------------------------------------
# op_alias (class decorator): attach an OpSpec alias to the model
# ---------------------------------------------------------------------------


def op_alias(
    *,
    alias: str,
    target: TargetOp,
    arity: Arity | None = None,
    persist: PersistPolicy = "default",
    request_model: SchemaArg | None = None,
    response_model: SchemaArg | None = None,
    http_methods: Sequence[str] | None = None,
    tags: Sequence[str] | None = None,
    rbac_guard_op: TargetOp | None = None,
):
    """Class decorator to declare an alias for an operation."""

    def deco(table_cls: type):
        ops = list(getattr(table_cls, "__tigrbl_ops__", ()))
        spec = OpSpec(
            alias=alias,
            target=target,
            table=table_cls,
            arity=arity or _infer_arity(target),
            persist=_normalize_persist(persist),
            request_model=request_model,
            response_model=response_model,
            http_methods=tuple(http_methods) if http_methods else None,
            tags=tuple(tags or ()),
            rbac_guard_op=rbac_guard_op,
        )
        ops.append(spec)
        table_cls.__tigrbl_ops__ = tuple(ops)
        return table_cls

    return deco


# ---------------------------------------------------------------------------
# op_ctx (single path: target + arity) with schema overrides
# ---------------------------------------------------------------------------


@dataclass
class _OpDecl:
    alias: Optional[str]
    target: Optional[TargetOp]
    arity: Optional[Arity]
    rest: Optional[bool]
    request_schema: Optional[SchemaArg]
    response_schema: Optional[SchemaArg]
    persist: Optional[PersistPolicy]
    status_code: Optional[int]


def op_ctx(
    *,
    bind: Any | Iterable[Any] | None = None,
    alias: Optional[str] = None,
    target: Optional[TargetOp] = None,
    arity: Optional[Arity] = None,
    rest: Optional[bool] = None,
    request_schema: Optional[SchemaArg] = None,
    response_schema: Optional[SchemaArg] = None,
    persist: Optional[PersistPolicy] = None,
    status_code: Optional[int] = None,
):
    """Declare a ctx-only operation whose body is `(cls, ctx)`."""

    def deco(fn):
        cm = _ensure_cm(fn)
        f = _unwrap(cm)
        f.__tigrbl_ctx_only__ = True
        f.__tigrbl_op_decl__ = _OpDecl(
            alias=alias,
            target=target,
            arity=arity,
            rest=rest,
            request_schema=request_schema,
            response_schema=response_schema,
            persist=persist,
            status_code=status_code,
        )

        if bind is not None:
            targets = (
                bind
                if isinstance(bind, Iterable) and not isinstance(bind, (str, bytes))
                else [bind]
            )
            for obj in targets:
                setattr(obj, f.__name__, cm)

        return cm

    return deco


# ---------------------------------------------------------------------------
# Collection helpers
# ---------------------------------------------------------------------------

_COLLECTION_VERBS = {
    "create",
    "list",
    "bulk_create",
    "bulk_update",
    "bulk_replace",
    "bulk_merge",
    "bulk_delete",
    "clear",
    "merge",
}


def _infer_arity(target: str) -> str:
    return "collection" if target in _COLLECTION_VERBS else "member"


def _normalize_persist(p) -> str:
    if p is None:
        return "default"
    p = str(p).lower()
    if p in {"none", "skip", "read"}:
        return "skip"
    if p in {"append"}:
        return "append"
    if p in {"override"}:
        return "override"
    if p in {"prepend"}:
        return "prepend"
    if p in {"write", "default", "persist"}:
        return "default"
    return "default"


__all__ = ["alias", "alias_ctx", "op_alias", "op_ctx"]
