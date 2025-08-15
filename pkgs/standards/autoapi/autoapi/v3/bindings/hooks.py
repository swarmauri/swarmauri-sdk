# autoapi/v3/bindings/hooks.py
from __future__ import annotations

import inspect
import logging
from types import SimpleNamespace
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)

from ..opspec import OpHook, OpSpec
from ..opspec.types import PHASES, StepFn
from ..config.constants import (
    CTX_SKIP_PERSIST_FLAG,
    API_HOOKS_ATTR,
    HOOKS_ATTR,
    IMPERATIVE_HOOKS_ATTR,
)

logger = logging.getLogger(__name__)

_Key = Tuple[str, str]  # (alias, target)


# ───────────────────────────────────────────────────────────────────────────────
# Phase groupings for precedence (mirrors v2 policy)
# pre-like: broad → specific
# post-like & errors: specific → broad
# ───────────────────────────────────────────────────────────────────────────────

_PRE_LIKE = frozenset({"PRE_TX_BEGIN", "START_TX", "PRE_HANDLER", "PRE_COMMIT"})
_POST_LIKE = frozenset({"POST_HANDLER", "POST_COMMIT", "POST_RESPONSE", "FINAL"})
_ERROR_LIKE = frozenset(
    {
        "ON_ROLLBACK",
        "ON_PRE_HANDLER_ERROR",
        "ON_HANDLER_ERROR",
        "ON_POST_HANDLER_ERROR",
        "ON_PRE_COMMIT_ERROR",
        # v3 uses END_TX; map v2's ON_COMMIT_ERROR → ON_END_TX_ERROR
        "ON_END_TX_ERROR",
        "ON_POST_COMMIT_ERROR",
        "ON_POST_RESPONSE_ERROR",
        "ON_ERROR",
    }
)


def _is_pre_like(p: str) -> bool:
    return p in _PRE_LIKE


def _is_post_or_error(p: str) -> bool:
    return p in _POST_LIKE or p in _ERROR_LIKE


# ───────────────────────────────────────────────────────────────────────────────
# ctx helpers
# ───────────────────────────────────────────────────────────────────────────────


def _ctx_get(ctx: Mapping[str, Any], key: str, default: Any = None) -> Any:
    try:
        return ctx[key]
    except Exception:
        return getattr(ctx, key, default)


def _ctx_db(ctx: Mapping[str, Any]) -> Any:
    return _ctx_get(ctx, "db")


def _ctx_payload(ctx: Mapping[str, Any]) -> Mapping[str, Any]:
    return _ctx_get(ctx, "payload", {}) or {}


def _is_async_db(db: Any) -> bool:
    return hasattr(db, "run_sync") or inspect.iscoroutinefunction(
        getattr(db, "commit", None)
    )


# ───────────────────────────────────────────────────────────────────────────────
# Default transactional steps
# ───────────────────────────────────────────────────────────────────────────────


def _default_start_tx() -> StepFn:
    async def _step(ctx: Any) -> None:
        db = _ctx_db(ctx)
        if db is None:
            return
        begin = getattr(db, "begin", None)
        if begin is None:
            return
        if _is_async_db(db):
            await begin()  # type: ignore[misc]
        else:
            begin()

    return _step


def _default_end_tx() -> StepFn:
    async def _step(ctx: Any) -> None:
        db = _ctx_db(ctx)
        if db is None:
            return
        commit = getattr(db, "commit", None)
        if commit is None:
            return
        if _is_async_db(db):
            await commit()  # type: ignore[misc]
        else:
            commit()

    return _step


def _mark_skip_persist() -> StepFn:
    async def _step(ctx: Any) -> None:
        try:
            ctx[CTX_SKIP_PERSIST_FLAG] = True
        except Exception:
            setattr(ctx, CTX_SKIP_PERSIST_FLAG, True)

    return _step


# ───────────────────────────────────────────────────────────────────────────────
# Step wrappers
# ───────────────────────────────────────────────────────────────────────────────


def _wrap_hook(h: OpHook) -> StepFn:
    fn = h.fn
    pred = h.when

    async def _step(ctx: Any) -> Any:
        if pred is not None:
            payload = _ctx_payload(ctx)
            try:
                ok = bool(pred(payload))
            except TypeError:
                ok = bool(pred(ctx))  # type: ignore[misc]
            except Exception:
                ok = True
            if not ok:
                return None
        rv = fn(ctx)
        if inspect.isawaitable(rv):
            return await rv
        return rv

    return _step


def _wrap_step_fn(fn: Callable[..., Any]) -> StepFn:
    async def _step(ctx: Any) -> Any:
        rv = fn(ctx)
        if inspect.isawaitable(rv):
            return await rv
        return rv

    return _step


# ───────────────────────────────────────────────────────────────────────────────
# Source collection (API / MODEL / OP / IMPERATIVE) for a single alias
# Accepted shapes for API/MODEL/IMPERATIVE sources:
#   • { phase: Iterable[callable] }                      (applies to all aliases)
#   • { alias: { phase: Iterable[callable] } }           (per-alias)
# ───────────────────────────────────────────────────────────────────────────────


def _to_phase_map_for_alias(source: Any, alias: str) -> Dict[str, List[StepFn]]:
    """
    Normalize a user-provided hooks source to { phase: [StepFn, ...], ... } for the given alias.
    """
    out: Dict[str, List[StepFn]] = {}
    if not source:
        return out

    # per-alias mapping?
    maybe = None
    if isinstance(source, Mapping):
        # If it looks like {alias: {...}}, pull per-alias or wildcard
        if alias in source:
            maybe = source.get(alias)
        elif "*" in source:
            maybe = source.get("*")
        else:
            # Could be a flat {phase: iter} map
            maybe = source

    if isinstance(maybe, Mapping):
        for ph, items in (maybe or {}).items():
            steps = out.setdefault(str(ph), [])
            if isinstance(items, Iterable):
                for fn in items:
                    if callable(fn):
                        steps.append(_wrap_step_fn(fn))
    return out


# ───────────────────────────────────────────────────────────────────────────────
# Precedence merge
# ───────────────────────────────────────────────────────────────────────────────


def _merge_for_phase(
    phase: str,
    *,
    api_map: Mapping[str, List[StepFn]] | None,
    model_map: Mapping[str, List[StepFn]] | None,
    op_map: Mapping[str, List[StepFn]] | None,
    imp_map: Mapping[str, List[StepFn]] | None,
) -> List[StepFn]:
    """
    Merge lists from sources for one phase using v2-compatible precedence policy:
      • pre-like  → API + MODEL + OP + IMPERATIVE
      • post/error→ IMPERATIVE + OP + MODEL + API
    """

    def _get(m: Mapping[str, List[StepFn]] | None) -> List[StepFn]:
        if not m:
            return []
        return list(m.get(phase, []) or [])

    if _is_pre_like(phase):
        return _get(api_map) + _get(model_map) + _get(op_map) + _get(imp_map)
    # post-like and errors
    return _get(imp_map) + _get(op_map) + _get(model_map) + _get(api_map)


# ───────────────────────────────────────────────────────────────────────────────
# Alias namespace helper
# ───────────────────────────────────────────────────────────────────────────────


def _ensure_alias_hooks_ns(model: type, alias: str) -> SimpleNamespace:
    root = getattr(model, "hooks", None)
    if root is None:
        root = SimpleNamespace()
        setattr(model, "hooks", root)
    ns = getattr(root, alias, None)
    if ns is None:
        ns = SimpleNamespace()
        setattr(root, alias, ns)
    # Ensure all known phases exist as lists
    for ph in PHASES:
        if not hasattr(ns, ph):
            setattr(ns, ph, [])
    return ns


# ───────────────────────────────────────────────────────────────────────────────
# Build / attach (with precedence)
# ───────────────────────────────────────────────────────────────────────────────


def _attach_one(model: type, sp: OpSpec) -> None:
    alias = sp.alias
    ns = _ensure_alias_hooks_ns(model, alias)

    # Reset existing chains for a clean rebuild
    for ph in PHASES:
        setattr(ns, ph, [])

    # Resolve source maps for this alias
    # API-level hooks may be injected by the API facade before binding:
    #   model.__autoapi_api_hooks__ = {phase:[...]} or {"*":{phase:[...]}, alias:{...}}
    api_src = getattr(model, API_HOOKS_ATTR, None)
    api_map = _to_phase_map_for_alias(api_src, alias)

    # Model/table-level defaults
    model_src = getattr(model, HOOKS_ATTR, None)
    model_map = _to_phase_map_for_alias(model_src, alias)

    # Op-level (from OpSpec.hooks)
    op_map: Dict[str, List[StepFn]] = {}
    for h in sp.hooks or ():
        phase = str(h.phase)
        op_map.setdefault(phase, []).append(_wrap_hook(h))

    # Imperative (runtime/registry) – same accepted shapes as API/MODEL
    imp_src = getattr(model, IMPERATIVE_HOOKS_ATTR, None)
    imp_map = _to_phase_map_for_alias(imp_src, alias)

    # Build per-phase chains via precedence merge
    for ph in PHASES:
        merged = _merge_for_phase(
            ph, api_map=api_map, model_map=model_map, op_map=op_map, imp_map=imp_map
        )

        # Inject default transactional steps (persistent ops only)
        if sp.persist != "skip":
            if ph == "START_TX":
                # default begin must be first
                merged = [_default_start_tx()] + merged
            if ph == "END_TX":
                # default commit must be last
                merged = merged + [_default_end_tx()]
        else:
            # Ephemeral: mark skip in PRE_TX_BEGIN and never add start/end
            if ph == "PRE_TX_BEGIN":
                merged = [_mark_skip_persist()] + merged

        setattr(ns, ph, merged)

    logger.debug(
        "hooks: %s.%s merged with precedence (persist=%s)",
        model.__name__,
        alias,
        sp.persist,
    )


def normalize_and_attach(
    model: type, specs: Sequence[OpSpec], *, only_keys: Optional[Sequence[_Key]] = None
) -> None:
    """
    Build sequential phase chains for each OpSpec and attach them to model.hooks.<alias>.
    If `only_keys` is provided, limit work to those (alias,target) pairs.

    Sources merged per phase (in precedence order):
      • PRE-like:   API → MODEL → OP → IMPERATIVE
      • POST/ERROR: IMPERATIVE → OP → MODEL → API
    """
    wanted = set(only_keys or ())
    for sp in specs:
        key = (sp.alias, sp.target)
        if wanted and key not in wanted:
            continue
        _attach_one(model, sp)


__all__ = ["normalize_and_attach"]
