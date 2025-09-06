from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Awaitable, Callable, Dict, Mapping, Sequence, Tuple

from .fastapi import Request
from ...op.types import PHASES

try:
    from ...runtime.kernel import build_phase_chains as _kernel_build_phase_chains  # type: ignore
except Exception:  # pragma: no cover
    _kernel_build_phase_chains = None  # type: ignore

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/rest/helpers")

_Key = Tuple[str, str]  # (alias, target)


def _ensure_jsonable(obj: Any) -> Any:
    """Best-effort conversion of DB rows, row-mappings, or ORM objects to dicts."""
    if isinstance(obj, (list, tuple)):
        return [_ensure_jsonable(x) for x in obj]

    if isinstance(obj, Mapping):
        try:
            return {k: _ensure_jsonable(v) for k, v in dict(obj).items()}
        except Exception:  # pragma: no cover - fall back to original object
            pass

    try:
        data = vars(obj)
    except TypeError:
        return obj

    return {k: _ensure_jsonable(v) for k, v in data.items() if not k.startswith("_")}


def _req_state_db(request: Request) -> Any:
    return getattr(request.state, "db", None)


def _resource_name(model: type) -> str:
    """
    Resource segment for HTTP paths/tags.

    IMPORTANT: Never use table name here. Only allow an explicit __resource__
    override or fall back to the model class name in lowercase.
    """
    override = getattr(model, "__resource__", None)
    return override or model.__name__.lower()


def _pk_name(model: type) -> str:
    """
    Single primary key name (fallback 'id'). For composite keys, still returns 'id'.
    Used for backward-compat path-param aliasing and handler resolution.
    """
    table = getattr(model, "__table__", None)
    if table is None:
        return "id"
    pk = getattr(table, "primary_key", None)
    if pk is None:
        return "id"
    try:
        cols = list(pk.columns)
    except Exception:
        return "id"
    if len(cols) != 1:
        return "id"
    return getattr(cols[0], "name", "id")


def _pk_names(model: type) -> set[str]:
    """All PK column names (fallback {'id'})."""
    table = getattr(model, "__table__", None)
    try:
        cols = getattr(getattr(table, "primary_key", None), "columns", None)
        if cols is None:
            return {"id"}
        out = {getattr(c, "name", None) for c in cols}
        out.discard(None)
        return out or {"id"}
    except Exception:
        return {"id"}


def _get_phase_chains(
    model: type, alias: str
) -> Dict[str, Sequence[Callable[..., Awaitable[Any]]]]:
    """
    Prefer building via runtime Kernel (atoms + system steps + hooks in one lifecycle).
    Fallback: read the pre-built model.hooks.<alias> chains directly.
    """
    if _kernel_build_phase_chains is not None:
        try:
            return _kernel_build_phase_chains(model, alias)
        except Exception:
            logger.exception(
                "Kernel build_phase_chains failed for %s.%s; falling back to hooks",
                getattr(model, "__name__", model),
                alias,
            )
    hooks_root = getattr(model, "hooks", None) or SimpleNamespace()
    alias_ns = getattr(hooks_root, alias, None)
    out: Dict[str, Sequence[Callable[..., Awaitable[Any]]]] = {}
    for ph in PHASES:
        out[ph] = list(getattr(alias_ns, ph, []) or [])
    return out


def _coerce_parent_kw(model: type, parent_kw: Dict[str, Any]) -> None:
    for name, val in list(parent_kw.items()):
        col = getattr(model, name, None)
        try:
            parent_kw[name] = col.type.python_type(val)  # type: ignore[attr-defined]
        except Exception:
            pass
