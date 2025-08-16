# autoapi/v3/decorators.py
from __future__ import annotations
import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Optional, Union

# Core types
from autoapi.v3.opspec.types import (
    OpSpec, Arity, TargetOp, PersistPolicy, SchemaArg,
)
from autoapi.v3.runtime.executor import _Ctx  # pipeline ctx normalizer

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
    if p.startswith("PRE_"): return "payload"
    if p.startswith("POST_"): return "result"
    if p.startswith("ON_"): return "error"
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
# schema_ctx (class decorator): register extra model-wide schemas
# ──────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class _SchemaDecl:
    alias: str                 # name under model.schemas.<alias>
    kind: str                  # "in" | "out"

def _register_schema_decl(target_model: type, alias: str, kind: str, schema_cls: type) -> None:
    """
    Store declarations directly on the model so we can attach them later during schema binding.
    Shape: model.__autoapi_schema_decls__ = { alias: {"in": cls, "out": cls, ...}, ... }
    """
    if kind not in ("in", "out"):
        raise ValueError("schema_ctx(kind=...) must be 'in' or 'out'")
    mapping: Dict[str, Dict[str, type]] = getattr(target_model, "__autoapi_schema_decls__", None) or {}
    bucket = dict(mapping.get(alias, {}))
    bucket[kind] = schema_cls
    mapping[alias] = bucket
    setattr(target_model, "__autoapi_schema_decls__", mapping)

def schema_ctx(*, alias: str, kind: str = "out", for_: Optional[type] = None):
    """
    Decorate a (Pydantic) class to register it as a named schema for a target model.

    Usage 1 (nested inside the model class):
        class Widget:
            @schema_ctx(alias="Search", kind="in")
            class SearchParams(BaseModel): ...

            @schema_ctx(alias="Search", kind="out")
            class SearchResult(BaseModel): ...

    Usage 2 (external class, explicit target):
        @schema_ctx(alias="Export", kind="out", for_=Widget)
        class ExportRow(BaseModel): ...

    The schema becomes addressable as:
        SchemaRef("Search", "in")   →  model.schemas.Search.in_
        SchemaRef("Search", "out")  →  model.schemas.Search.out
    """
    def deco(schema_cls: type):
        if not isinstance(schema_cls, type):
            raise TypeError("@schema_ctx must decorate a class")

        # If explicit model provided, register immediately on that model
        if for_ is not None:
            _register_schema_decl(for_, alias, kind, schema_cls)

        # Always mark the schema class so we can pick it up if it's nested in the model
        setattr(schema_cls, "__autoapi_schema_decl__", _SchemaDecl(alias=alias, kind=kind))
        return schema_cls
    return deco

def collect_decorated_schemas(model: type) -> Dict[str, Dict[str, type]]:
    """
    Gather all schema declarations for a model, merging:
      • Explicit registrations via schema_ctx(..., for_=Model)
      • Nested class declarations inside the model (and its bases)
    Subclass declarations override base-class ones for the same (alias, kind).
    """
    out: Dict[str, Dict[str, type]] = {}

    # 1) Explicit registrations (MRO-merged)
    for base in reversed(model.__mro__):
        mapping: Dict[str, Dict[str, type]] = getattr(base, "__autoapi_schema_decls__", {}) or {}
        for alias, kinds in mapping.items():
            bucket = out.setdefault(alias, {})
            bucket.update(kinds or {})

    # 2) Nested classes with __autoapi_schema_decl__
    for base in reversed(model.__mro__):
        for name in dir(base):
            obj = getattr(base, name, None)
            if not inspect.isclass(obj):
                continue
            decl: _SchemaDecl | None = getattr(obj, "__autoapi_schema_decl__", None)
            if not decl:
                continue
            bucket = out.setdefault(decl.alias, {})
            bucket[decl.kind] = obj

    return out


# ──────────────────────────────────────────────────────────────────────
# op_ctx (single path: target + arity) with schema overrides
# ──────────────────────────────────────────────────────────────────────

@dataclass
class _OpDecl:
    alias: Optional[str]
    target: Optional[TargetOp]            # canonical semantics (defaults to "custom")
    arity: Optional[Arity]                # "member" | "collection"
    rest: Optional[bool]                  # toggle REST exposure
    request_schema: Optional[SchemaArg]   # lazy-capable schema override
    response_schema: Optional[SchemaArg]
    persist: Optional[PersistPolicy]      # TX policy override

def op_ctx(
    *,
    alias: Optional[str] = None,
    target: Optional[TargetOp] = None,             # "create" | "read" | ... | "custom"
    arity: Optional[Arity] = None,                 # "member" | "collection"
    rest: Optional[bool] = None,
    request_schema: Optional[SchemaArg] = None,
    response_schema: Optional[SchemaArg] = None,
    persist: Optional[PersistPolicy] = None,
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
        )
        return cm
    return deco


# ──────────────────────────────────────────────────────────────────────
# hook_ctx
# ──────────────────────────────────────────────────────────────────────

@dataclass
class _HookDecl:
    ops: Union[str, Iterable[str]]  # alias names, canonical verbs, or "*"
    phase: str                      # e.g., "PRE_HANDLER", "POST_COMMIT", "ON_HANDLER_ERROR"

def hook_ctx(ops: Union[str, Iterable[str]], *, phase: str):
    """
    Declare a ctx-only hook for one/many ops at a given phase. Method is `(cls, ctx)`.
    `ops` can be {"create", "update"} or {"my_alias"} or "*" for all visible ops.
    """
    def deco(fn):
        cm = _ensure_cm(fn)
        f = _unwrap(cm)
        f.__autoapi_ctx_only__ = True
        lst = getattr(f, "__autoapi_hook_decls__", [])
        lst.append(_HookDecl(ops, phase))
        f.__autoapi_hook_decls__ = lst
        return cm
    return deco


# ──────────────────────────────────────────────────────────────────────
# Adapters: ctx-only → pipeline signatures
# ──────────────────────────────────────────────────────────────────────

def _wrap_ctx_core(table: type, func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Adapt `(cls, ctx)` op to `(p, *, db, request, ctx)` handler signature.
    """
    async def core(p=None, *, db=None, request=None, ctx: Dict[str, Any] | None = None):
        ctx = _Ctx.ensure(ctx)
        if p is not None: ctx["payload"] = p
        if db is not None: ctx["db"] = db
        if request is not None: ctx["request"] = request
        bound = func.__get__(table, table)
        res = await _maybe_await(bound(ctx))
        return res if res is not None else ctx.get("result")
    return core

def _wrap_ctx_hook(table: type, func: Callable[..., Any], phase: str) -> Callable[..., Any]:
    """
    Adapt `(cls, ctx)` hook to `(value?, *, db, request, ctx)` hook signature.
    """
    io_key = _phase_io_key(phase)
    async def hook(value=None, *, db=None, request=None, ctx: Dict[str, Any] | None = None):
        ctx = _Ctx.ensure(ctx)
        if db is not None: ctx["db"] = db
        if request is not None: ctx["request"] = request
        if io_key is not None and value is not None:
            ctx[io_key] = value
        bound = func.__get__(table, table)
        _ = await _maybe_await(bound(ctx))
        if io_key is None:
            return None
        return ctx.get(io_key, value)
    return hook


# ──────────────────────────────────────────────────────────────────────
# Collection helpers (called by bind)
# ──────────────────────────────────────────────────────────────────────

_COLLECTION_VERBS = {
    "list", "bulk_create", "bulk_update", "bulk_replace", "bulk_delete", "clear"
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
        for name in dir(base):
            attr = getattr(base, name, None)
            func = _unwrap(attr)
            decl: _OpDecl | None = getattr(func, "__autoapi_op_decl__", None)
            if not decl:
                continue

            target = decl.target or "custom"
            arity = decl.arity or _infer_arity(target)
            persist = _normalize_persist(decl.persist)
            alias = decl.alias or name

            expose_kwargs = {}
            if decl.rest is not None:
                expose_kwargs["expose_routes"] = bool(decl.rest)

            spec = OpSpec(
                table=table,
                alias=alias,
                target=target,                 # canonical verb
                arity=arity,
                persist=persist,
                handler=_wrap_ctx_core(table, func),
                request_model=decl.request_schema,
                response_model=decl.response_schema,
                hooks=(),
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
            decls: list[_HookDecl] | None = getattr(func, "__autoapi_hook_decls__", None)
            if not decls:
                continue
            for d in decls:
                for op in _resolve_ops(d.ops):
                    if op not in visible_aliases:
                        continue
                    ph = d.phase
                    mapping.setdefault(op, {}).setdefault(ph, []).append(
                        _wrap_ctx_hook(table, func, ph)
                    )
    return mapping
