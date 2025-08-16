# autoapi/v3/decorators.py
from __future__ import annotations
import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Optional, Union

# Core types
from autoapi.v3.opspec.types import (
    OpSpec, Arity, TargetOp, PersistPolicy, ReturnForm,
)
from autoapi.v3.runtime.executor import _Ctx  # pipeline ctx normalizer


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
# Public decorators (ctx-only)
# ──────────────────────────────────────────────────────────────────────

def alias_ctx(**aliases: str):
    """
    Class decorator to map canonical verbs → aliases.
    Example: @alias_ctx(create="add", read="get", update="patch")
    """
    def deco(cls: type):
        existed = dict(getattr(cls, "__autoapi_aliases__", {}) or {})
        existed.update(aliases)
        setattr(cls, "__autoapi_aliases__", existed)
        return cls
    return deco


@dataclass
class _OpDecl:
    alias: Optional[str]
    verb: Optional[str]
    target: Union[str, TargetOp, None]
    returns: Union[str, ReturnForm, None]
    persist: Union[str, PersistPolicy, None]
    arity: Union[str, Arity, None]
    rest: Optional[bool]


def op_ctx(
    *,
    alias: str | None = None,
    verb: Optional[str] = "custom",            # required: "create" | "read" | "update" | "replace" | "delete" | "list" | ...
    target: TargetOp | str | None = None,      # default inferred from verb
    returns: ReturnForm | str | None = None,   # default inferred from verb
    persist: PersistPolicy | str | None = None,# default inferred from verb
    arity: Arity | str | None = None,          # default inferred from verb/target
    rest: bool | None = None,                  # None → default REST mapping
):
    """
    Declare a ctx-only custom operation. The method body is `(cls, ctx)`.
    """
    def deco(fn):
        cm = _ensure_cm(fn)
        f = _unwrap(cm)
        f.__autoapi_ctx_only__ = True
        f.__autoapi_op_decl__ = _OpDecl(alias, verb, target, returns, persist, arity, rest)
        return cm
    return deco


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

# --- add near your other helpers ---
_COLLECTION_VERBS = {"list", "bulk_create", "bulk_update", "bulk_replace", "bulk_delete", "clear"}

def _infer_arity(verb: str) -> str:
    return "collection" if verb in _COLLECTION_VERBS else "member"

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


def _infer_target(verb: str) -> str:
    return "collection" if verb in _COLLECTION_VERBS else "member"

def _infer_returns(verb: str, target: str) -> str:
    if verb == "list": return "rows"
    if verb.startswith("bulk_"): return "count"
    if verb in {"delete", "clear"}: return "ok"
    return "row"

def _infer_persist(verb: str) -> str:
    return "read" if verb in {"read", "list"} else "write"

def alias_map_for(table: type) -> Dict[str, str]:
    """Merge aliases across MRO; subclass wins."""
    return _merge_mro_dict(table, "__autoapi_aliases__")

def apply_alias(verb: str, alias_map: Dict[str, str]) -> str:
    """Resolve canonical verb → alias (falls back to verb)."""
    return alias_map.get(verb, verb)

def collect_decorated_ops(table: type) -> list[OpSpec]:
    """
    Scan MRO for ctx-only op declarations (@op_ctx) and build OpSpecs.
    - decorator 'verb' is the canonical verb ('create','read','update','...')
    - decorator 'target' is treated as:
        • arity if in {'member','collection'}
        • canonical verb if it matches a canonical verb (fallback if verb=None)
    - 'rest' toggles expose_routes; we don't pass an unknown 'rest' kwarg to OpSpec.
    """
    out: list[OpSpec] = []

    for base in reversed(table.__mro__):
        for name in dir(base):
            attr = getattr(base, name, None)
            func = _unwrap(attr)
            decl = getattr(func, "__autoapi_op_decl__", None)
            if not decl:
                continue

            # 1) Canonical verb (TargetOp)
            verb = decl.verb
            # allow target to stand in for verb if it's a canonical verb string
            if verb is None and isinstance(decl.target, str) and decl.target in {
                "create","read","update","replace","delete","list","clear",
                "bulk_create","bulk_update","bulk_replace","bulk_delete","custom",
            }:
                verb = decl.target
            if verb is None:
                verb = "custom"  # safe default

            # 2) Arity (member/collection)
            if isinstance(decl.target, str) and decl.target in {"member", "collection"}:
                arity = decl.target
            else:
                arity = decl.arity or _infer_arity(verb)

            # 3) Persist & returns
            persist = _normalize_persist(decl.persist)
            returns = decl.returns or "raw"  # default to raw for ctx-only ops

            # 4) Alias (explicit or method name)
            alias = decl.alias or name

            # 5) Optional REST exposure flag from 'rest'
            expose_kwargs = {}
            if decl.rest is not None:
                expose_kwargs["expose_routes"] = bool(decl.rest)

            # 6) Build OpSpec
            spec = OpSpec(
                table=table,
                alias=alias,
                target=verb,          # canonical verb
                arity=arity,
                persist=persist,
                returns=returns,
                handler=_wrap_ctx_core(table, func),  # <-- custom core goes here
                hooks=(),             # hook_ctx handled separately
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
