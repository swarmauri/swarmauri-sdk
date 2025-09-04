# autoapi/v3/decorators.py
from __future__ import annotations
import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Optional, Union, Sequence

# Core types
from autoapi.v3.ops.types import (
    OpSpec,
    Arity,
    TargetOp,
    PersistPolicy,
)
from autoapi.v3.schema.types import SchemaArg
from autoapi.v3.schema.decorators import schema_ctx
from autoapi.v3.runtime.executor import _Ctx  # pipeline ctx normalizer
from .hook import HOOK_DECLS_ATTR, Hook, hook_ctx  # noqa: F401
from autoapi.v3.engine.decorators import engine_ctx

# Try-pydantic (optional; schemas may be any class but we keep this for hints/debug)
try:  # pragma: no cover
    from pydantic import BaseModel  # type: ignore
except Exception:  # pragma: no cover

    class BaseModel:  # minimal stub for typing only
        pass


# ──────────────────────────────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────────────────────────────


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


def _phase_io_key(phase: str) -> Optional[str]:
    p = str(phase)
    if p.startswith("PRE_"):
        return "payload"
    if p.startswith("POST_"):
        return "result"
    if p.startswith("ON_"):
        return "error"
    return None


def _merge_mro_dict(cls: type, attr: str) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    for base in reversed(cls.__mro__):
        merged.update(getattr(base, attr, {}) or {})
    return merged


# ──────────────────────────────────────────────────────────────────────
# alias_ctx with optional rich overrides
# ──────────────────────────────────────────────────────────────────────


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
    """
    Class decorator to map canonical verbs → aliases and (optionally) attach overrides.

    Examples:
        @alias_ctx(create="add", read="get")
        @alias_ctx(create=alias("add",
                                request_schema="create.in",
                                response_schema="read.out",
                                arity="collection",
                                rest=True))
    """

    def deco(cls: type):
        # plain alias map (verb -> alias)
        amap = dict(getattr(cls, "__autoapi_aliases__", {}) or {})
        # rich overrides keyed by canonical verb
        overrides = dict(getattr(cls, "__autoapi_alias_overrides__", {}) or {})

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

        setattr(cls, "__autoapi_aliases__", amap)
        setattr(cls, "__autoapi_alias_overrides__", overrides)
        return cls

    return deco


# ──────────────────────────────────────────────────────────────────────
# op_alias (class decorator): attach an OpSpec alias to the model
# ──────────────────────────────────────────────────────────────────────


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
    """Class decorator to declare an alias for an operation.

    Mirrors the v2 ``op_alias`` helper and attaches an :class:`OpSpec` to
    ``__autoapi_ops__`` on the target model.
    """

    def deco(table_cls: type):
        ops = list(getattr(table_cls, "__autoapi_ops__", ()))
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
        table_cls.__autoapi_ops__ = tuple(ops)
        return table_cls

    return deco


# ──────────────────────────────────────────────────────────────────────
# op_ctx (single path: target + arity) with schema overrides
# ──────────────────────────────────────────────────────────────────────


@dataclass
class _OpDecl:
    alias: Optional[str]
    target: Optional[TargetOp]  # canonical semantics (defaults to "custom")
    arity: Optional[Arity]  # "member" | "collection"
    rest: Optional[bool]  # toggle REST exposure
    request_schema: Optional[SchemaArg]  # lazy-capable schema override
    response_schema: Optional[SchemaArg]
    persist: Optional[PersistPolicy]  # TX policy override
    status_code: Optional[int]


def op_ctx(
    *,
    bind: Any | Iterable[Any] | None = None,
    alias: Optional[str] = None,
    target: Optional[TargetOp] = None,  # "create" | "read" | ... | "custom"
    arity: Optional[Arity] = None,  # "member" | "collection"
    rest: Optional[bool] = None,
    request_schema: Optional[SchemaArg] = None,
    response_schema: Optional[SchemaArg] = None,
    persist: Optional[PersistPolicy] = None,
    status_code: Optional[int] = None,
):
    """
    Declare a ctx-only operation whose body is `(cls, ctx)`.

    • `target` controls canonical semantics (default "custom").
    • `arity` controls REST path shape.
    • `request_schema` / `response_schema` can reference existing schemas (via SchemaRef or dotted).
    • If no response schema is resolved at bind time, the op is treated as returning raw.
    """

    def deco(fn):
        cm = _ensure_cm(fn)
        f = _unwrap(cm)
        f.__autoapi_ctx_only__ = True
        f.__autoapi_op_decl__ = _OpDecl(
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


# ──────────────────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────
# Adapters: ctx-only → pipeline signatures
# ──────────────────────────────────────────────────────────────────────


def _wrap_ctx_core(table: type, func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Adapt `(cls, ctx)` op to `(p, *, db, request, ctx)` handler signature.
    """

    async def core(p=None, *, db=None, request=None, ctx: Dict[str, Any] | None = None):
        ctx = _Ctx.ensure(request=request, db=db, seed=ctx)
        if p is not None:
            ctx["payload"] = p
        bound = func.__get__(table, table)
        res = await _maybe_await(bound(ctx))
        return res if res is not None else ctx.get("result")

    core.__name__ = getattr(func, "__name__", "core")
    core.__qualname__ = getattr(func, "__qualname__", core.__name__)
    return core


def _wrap_ctx_hook(
    table: type, func: Callable[..., Any], phase: str
) -> Callable[..., Any]:
    """
    Adapt `(cls, ctx)` hook to `(value?, *, db, request, ctx)` hook signature.
    """
    io_key = _phase_io_key(phase)

    async def hook(
        value=None, *, db=None, request=None, ctx: Dict[str, Any] | None = None
    ):
        ctx = _Ctx.ensure(request=request, db=db, seed=ctx)
        if io_key is not None and value is not None:
            ctx[io_key] = value
        bound = func.__get__(table, table)
        _ = await _maybe_await(bound(ctx))
        if io_key is None:
            return None
        return ctx.get(io_key, value)

    hook.__name__ = getattr(func, "__name__", "hook")
    hook.__qualname__ = getattr(func, "__qualname__", hook.__name__)
    return hook


# ──────────────────────────────────────────────────────────────────────
# Collection helpers (called by bind)
# ──────────────────────────────────────────────────────────────────────

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
    if p in {"write", "default", "persist"}:
        return "default"
    if p == "override":
        return "override"
    return "default"


def alias_map_for(table: type) -> Dict[str, str]:
    """Merge aliases across MRO; subclass wins."""
    return _merge_mro_dict(table, "__autoapi_aliases__")


def apply_alias(verb: str, alias_map: Dict[str, str]) -> str:
    """Resolve canonical verb → alias (falls back to verb)."""
    return alias_map.get(verb, verb)


def collect_decorated_ops(table: type) -> list[OpSpec]:
    """
    Scan MRO for ctx-only op declarations (@op_ctx) and build OpSpecs.

    Normalization:
      • `target` is the canonical verb ("create","read","...", default "custom").
      • `arity` is "member"/"collection". If omitted, inferred from target.
      • `rest` toggles `expose_routes` on the spec.
    """
    out: list[OpSpec] = []

    for base in reversed(table.__mro__):
        names = list(getattr(base, "__dict__", {}).keys())
        for name in dir(base):
            if name not in names:
                names.append(name)
        for name in names:
            attr = getattr(base, name, None)
            func = _unwrap(attr)
            decl: _OpDecl | None = getattr(func, "__autoapi_op_decl__", None)
            if not decl:
                continue

            target = decl.target or "custom"
            arity = decl.arity or _infer_arity(target)
            persist = _normalize_persist(decl.persist)
            alias = decl.alias or name

            expose_kwargs: dict[str, Any] = {}
            extra: dict[str, Any] = {}
            if decl.rest is not None:
                expose_kwargs["expose_routes"] = bool(decl.rest)
            elif alias != target and target in {
                "read",
                "update",
                "delete",
                "list",
                "clear",
            }:
                expose_kwargs["expose_routes"] = False

            spec = OpSpec(
                table=table,
                alias=alias,
                target=target,  # canonical verb
                arity=arity,
                persist=persist,
                handler=_wrap_ctx_core(table, func),
                request_model=decl.request_schema,
                response_model=decl.response_schema,
                hooks=(),
                status_code=decl.status_code,
                extra=extra,
                **expose_kwargs,
            )
            out.append(spec)

    return out


def collect_decorated_hooks(
    table: type,
    *,
    visible_aliases: set[str],
) -> Dict[str, Dict[str, list[Callable[..., Any]]]]:
    """
    Build alias→phase→[hook] map. Supports ops as alias names, canonical verbs, or "*".
    Canonical verbs are resolved using the class alias map.
    """
    mapping: Dict[str, Dict[str, list[Callable[..., Any]]]] = {}
    aliases = alias_map_for(table)

    def _resolve_ops(spec: Union[str, Iterable[str]]) -> Iterable[str]:
        if spec == "*":
            return visible_aliases
        if isinstance(spec, str):
            return [spec if spec in visible_aliases else apply_alias(spec, aliases)]
        out: list[str] = []
        for x in spec:
            out.append(x if x in visible_aliases else apply_alias(x, aliases))
        return out

    for base in reversed(table.__mro__):
        for name in dir(base):
            attr = getattr(base, name, None)
            func = _unwrap(attr)
            decls: list[Hook] | None = getattr(func, HOOK_DECLS_ATTR, None)
            if not decls:
                continue
            for d in decls:
                for op in _resolve_ops(d.ops):
                    if op not in visible_aliases:
                        continue
                    ph = d.phase
                    mapping.setdefault(op, {}).setdefault(ph, []).append(
                        _wrap_ctx_hook(table, d.fn, ph)
                    )
    return mapping


__all__ = [
    "alias",
    "alias_ctx",
    "op_alias",
    "schema_ctx",
    "hook_ctx",
    "engine_ctx",
    "op_ctx",
]
