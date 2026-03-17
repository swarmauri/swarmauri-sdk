"""Operation-related decorators for Tigrbl v3."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional, Sequence, Union

from .._spec.op_spec import OpSpec, Arity, TargetOp, PersistPolicy
from tigrbl_core._spec.op_utils import (
    _maybe_await as _core_maybe_await,
    _normalize_persist as _core_normalize_persist,
    _unwrap as _core_unwrap,
)
from .._spec.schema_spec import SchemaArg


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _unwrap(obj: Any) -> Callable[..., Any]:
    """Get underlying function for (class|static)method; else return obj."""
    return _core_unwrap(obj)


def _ensure_cm(func: Any) -> Any:
    """Ensure method is a classmethod so it receives (cls, ctx)."""
    if isinstance(func, (classmethod, staticmethod)):
        return func
    return classmethod(func)


def _maybe_await(v):
    return _core_maybe_await(v)


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
        # Alias maps are rebuilt from class metadata at bind-time.
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
):
    """Class decorator to declare an alias for an operation."""

    def deco(table_cls: type):
        ops = list(getattr(table_cls, "__tigrbl_ops__", ()))
        inferred_arity = arity or _infer_arity(target)
        if arity is None and target == "custom" and table_cls.__name__.endswith("App"):
            inferred_arity = "collection"

        spec = OpSpec(
            alias=alias,
            target=target,
            table=table_cls,
            arity=inferred_arity,
            persist=_normalize_persist(persist),
            request_model=request_model,
            response_model=response_model,
            http_methods=tuple(http_methods) if http_methods else None,
            tags=tuple(tags or ()),
        )
        ops.append(spec)
        table_cls.__tigrbl_ops__ = tuple(ops)
        return table_cls

    return deco


# ---------------------------------------------------------------------------
# op_ctx (single path: target + arity) with schema overrides
# ---------------------------------------------------------------------------


def op_ctx(
    *,
    bind: Any | Iterable[Any] | None = None,
    alias: Optional[str] = None,
    target: Optional[TargetOp] = None,
    arity: Optional[Arity] = None,
    http_methods: Sequence[str] | None = None,
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
        resolved_target = target or "custom"
        inferred_arity = arity or _infer_arity(resolved_target)
        if (
            arity is None
            and resolved_target == "custom"
            and bind is not None
            and any(
                isinstance(obj, type) and obj.__name__.endswith("App")
                for obj in (
                    bind
                    if isinstance(bind, Iterable) and not isinstance(bind, (str, bytes))
                    else [bind]
                )
            )
        ):
            inferred_arity = "collection"

        resolved_alias = alias or (
            resolved_target if resolved_target != "custom" else f.__name__
        )

        spec = OpSpec(
            alias=resolved_alias,
            target=resolved_target,
            arity=inferred_arity,
            http_methods=tuple(http_methods) if http_methods else None,
            expose_routes=True if rest is None else bool(rest),
            request_model=request_schema,
            response_model=response_schema,
            persist=_normalize_persist(persist),
            status_code=status_code,
        )
        f.__tigrbl_op_spec__ = spec
        # Backward-compatible attr name; value is always OpSpec.
        f.__tigrbl_op_decl__ = spec

        if bind is not None:
            targets = (
                bind
                if isinstance(bind, Iterable) and not isinstance(bind, (str, bytes))
                else [bind]
            )
            for obj in targets:
                setattr(obj, f.__name__, cm)
                if hasattr(obj, "ops"):
                    from tigrbl_concrete._mapping.model import rebind

                    rebind(obj)

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
    if target == "custom":
        return "collection"
    return "collection" if target in _COLLECTION_VERBS else "member"


def _normalize_persist(p) -> str:
    return _core_normalize_persist(p)


__all__ = ["alias", "alias_ctx", "op_alias", "op_ctx"]
