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
    AUTOAPI_API_HOOKS_ATTR,
    AUTOAPI_HOOKS_ATTR,
    CTX_SKIP_PERSIST_FLAG,
)

logger = logging.getLogger(__name__)

_Key = Tuple[str, str]  # (alias, target)

# ───────────────────────────────────────────────────────────────────────────────
# Phase groupings (v2-compatible precedence)
#   pre-like:    API → MODEL → OP
#   post/error:  OP  → MODEL → API
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
    v = _ctx_get(ctx, "payload", None)
    return v if v is not None else {}


# ───────────────────────────────────────────────────────────────────────────────
# System steps (conceptually distinct; injected for lifecycle completeness)
# ───────────────────────────────────────────────────────────────────────────────


def _default_start_tx() -> StepFn:
    async def _step(ctx: Any) -> None:
        db = _ctx_db(ctx)
        if db is None:
            return
        begin = getattr(db, "begin", None)
        if begin is None:
            return
        rv = begin()
        if inspect.isawaitable(rv):
            await rv  # type: ignore[misc]

    _step.__name__ = "start_tx"
    _step.__qualname__ = "start_tx"
    return _step


def _default_end_tx() -> StepFn:
    async def _step(ctx: Any) -> None:
        db = _ctx_db(ctx)
        if db is None:
            return
        commit = getattr(db, "commit", None)
        if commit is None:
            return
        rv = commit()
        if inspect.isawaitable(rv):
            await rv  # type: ignore[misc]

    _step.__name__ = "end_tx"
    _step.__qualname__ = "end_tx"
    return _step


def _mark_skip_persist() -> StepFn:
    async def _step(ctx: Any) -> None:
        try:
            ctx[CTX_SKIP_PERSIST_FLAG] = True
        except Exception:
            setattr(ctx, CTX_SKIP_PERSIST_FLAG, True)

    _step.__name__ = "mark_skip_persist"
    _step.__qualname__ = "mark_skip_persist"
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

            # Evaluate predicate without ever boolean-testing SQLAlchemy clauses.
            def _as_bool(val: object) -> bool:
                if isinstance(val, bool):
                    return val
                try:
                    return bool(val)
                except TypeError:
                    # e.g., SQLAlchemy ClauseElement: no boolean value → treat as pass
                    return True

            try:
                res = pred(payload)
            except TypeError:
                # Signature mismatch? Try with ctx.
                try:
                    res = pred(ctx)  # type: ignore[misc]
                except Exception:
                    res = True
            except Exception:
                res = True
            if not _as_bool(res):
                return None
        rv = fn(ctx)
        if inspect.isawaitable(rv):
            return await rv
        return rv

    _step.__name__ = getattr(fn, "__name__", _step.__name__)
    _step.__qualname__ = getattr(fn, "__qualname__", _step.__name__)
    return _step


def _wrap_step_fn(fn: Callable[..., Any]) -> StepFn:
    async def _step(ctx: Any) -> Any:
        rv = fn(ctx)
        if inspect.isawaitable(rv):
            return await rv
        return rv

    _step.__name__ = getattr(fn, "__name__", _step.__name__)
    _step.__qualname__ = getattr(fn, "__qualname__", _step.__name__)
    return _step


# ───────────────────────────────────────────────────────────────────────────────
# Source collection (API / MODEL / OP) for a single alias
# Accepted shapes for API/MODEL sources:
#   • { phase: Iterable[callable] }                    (applies to all aliases)
#   • { alias: { phase: Iterable[callable] } }         (per-alias)
# ───────────────────────────────────────────────────────────────────────────────


def _to_phase_map_for_alias(source: Any, alias: str) -> Dict[str, List[StepFn]]:
    """
    Normalize a user-provided hooks source to { phase: [StepFn, ...], ... } for the given alias.
    """
    out: Dict[str, List[StepFn]] = {}
    if not source:
        return out

    maybe = None
    if isinstance(source, Mapping):
        if alias in source:
            maybe = source.get(alias)
        elif "*" in source:
            maybe = source.get("*")
        else:
            maybe = source  # flat {phase: iterable}

    if isinstance(maybe, Mapping):
        for ph, items in (maybe or {}).items():
            steps = out.setdefault(str(ph), [])
            if isinstance(items, Iterable):
                for fn in items:
                    if callable(fn):
                        steps.append(_wrap_step_fn(fn))
    return out


# ───────────────────────────────────────────────────────────────────────────────
# Precedence merge (API/MODEL/OP only; no imperative source)
# ───────────────────────────────────────────────────────────────────────────────


def _merge_for_phase(
    phase: str,
    *,
    api_map: Mapping[str, List[StepFn]] | None,
    model_map: Mapping[str, List[StepFn]] | None,
    op_map: Mapping[str, List[StepFn]] | None,
) -> List[StepFn]:
    """
    Merge lists from sources for one phase:
      • pre-like  → API + MODEL + OP
      • post/error→ OP + MODEL + API
    """

    def _get(m: Mapping[str, List[StepFn]] | None) -> List[StepFn]:
        if not m:
            return []
        return list(m.get(phase, []) or [])

    if _is_pre_like(phase):
        return _get(api_map) + _get(model_map) + _get(op_map)
    return _get(op_map) + _get(model_map) + _get(api_map)


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
    api_src = getattr(model, AUTOAPI_API_HOOKS_ATTR, None)
    model_src = getattr(model, AUTOAPI_HOOKS_ATTR, None)

    api_map = _to_phase_map_for_alias(api_src, alias)
    model_map = _to_phase_map_for_alias(model_src, alias)

    # Op-level (from OpSpec.hooks)
    op_map: Dict[str, List[StepFn]] = {}
    for h in sp.hooks or ():
        phase = str(h.phase)
        op_map.setdefault(phase, []).append(_wrap_hook(h))

    # Build per-phase chains via precedence merge
    for ph in PHASES:
        merged = _merge_for_phase(
            ph, api_map=api_map, model_map=model_map, op_map=op_map
        )

        # Inject default transactional steps (system steps; distinct concept)
        if sp.persist != "skip":
            if ph == "START_TX":
                merged = [_default_start_tx()] + merged  # begin must be first
            if ph == "END_TX":
                merged = merged + [_default_end_tx()]  # commit must be last
        else:
            # Ephemeral: mark skip in PRE_TX_BEGIN; no START/END
            if ph == "PRE_TX_BEGIN":
                merged = [_mark_skip_persist()] + merged

        setattr(ns, ph, merged)

    logger.debug("hooks: %s.%s merged (persist=%s)", model.__name__, alias, sp.persist)


def normalize_and_attach(
    model: type, specs: Sequence[OpSpec], *, only_keys: Optional[Sequence[_Key]] = None
) -> None:
    """
    Build sequential phase chains for each OpSpec and attach them to model.hooks.<alias>.
    Sources merged per phase (in precedence order):
      • PRE-like:   API → MODEL → OP
      • POST/ERROR: OP  → MODEL → API
    """
    wanted = set(only_keys or ())
    for sp in specs:
        key = (sp.alias, sp.target)
        if wanted and key not in wanted:
            continue
        _attach_one(model, sp)


__all__ = ["normalize_and_attach"]
