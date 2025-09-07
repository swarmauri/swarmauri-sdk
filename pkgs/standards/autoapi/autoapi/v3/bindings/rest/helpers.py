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

logging.getLogger("uvicorn").setLevel(logging.DEBUG)
logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/rest/helpers")

_Key = Tuple[str, str]  # (alias, target)


def _ensure_jsonable(obj: Any) -> Any:
    """Best-effort conversion of DB rows, row-mappings, or ORM objects to dicts."""
    logger.debug("_ensure_jsonable type=%s", type(obj))
    if isinstance(obj, (list, tuple)):
        logger.debug("converting sequence of length %d", len(obj))
        return [_ensure_jsonable(x) for x in obj]

    if isinstance(obj, Mapping):
        try:
            logger.debug("converting mapping with %d keys", len(obj))
            return {k: _ensure_jsonable(v) for k, v in dict(obj).items()}
        except Exception:
            logger.debug("mapping conversion failed", exc_info=True)
            pass

    try:
        data = vars(obj)
    except TypeError:
        logger.debug("object not introspectable; returning as-is")
        return obj

    return {k: _ensure_jsonable(v) for k, v in data.items() if not k.startswith("_")}


def _req_state_db(request: Request) -> Any:
    db = getattr(request.state, "db", None)
    logger.debug("_req_state_db -> %s", db)
    return db


def _resource_name(model: type) -> str:
    """
    Resource segment for HTTP paths/tags.

    IMPORTANT: Never use table name here. Only allow an explicit __resource__
    override or fall back to the model class name in lowercase.
    """
    override = getattr(model, "__resource__", None)
    result = override or model.__name__.lower()
    logger.debug("_resource_name %s -> %s", model, result)
    return result


def _pk_name(model: type) -> str:
    """
    Single primary key name (fallback 'id'). For composite keys, still returns 'id'.
    Used for backward-compat path-param aliasing and handler resolution.
    """
    table = getattr(model, "__table__", None)
    if table is None:
        logger.debug("_pk_name no table for %s", model)
        return "id"
    pk = getattr(table, "primary_key", None)
    if pk is None:
        logger.debug("_pk_name no pk for %s", model)
        return "id"
    try:
        cols = list(pk.columns)
    except Exception:
        logger.debug("_pk_name pk introspection failed for %s", model)
        return "id"
    if len(cols) != 1:
        logger.debug("_pk_name composite pk for %s", model)
        return "id"
    name = getattr(cols[0], "name", "id")
    logger.debug("_pk_name %s -> %s", model, name)
    return name


def _pk_names(model: type) -> set[str]:
    """All PK column names (fallback {'id'})."""
    table = getattr(model, "__table__", None)
    try:
        cols = getattr(getattr(table, "primary_key", None), "columns", None)
        if cols is None:
            logger.debug("_pk_names no cols for %s", model)
            return {"id"}
        out = {getattr(c, "name", None) for c in cols}
        out.discard(None)
        result = out or {"id"}
        logger.debug("_pk_names %s -> %s", model, result)
        return result
    except Exception:
        logger.debug("_pk_names failed for %s", model, exc_info=True)
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
            logger.debug("building phase chains via kernel for %s.%s", model, alias)
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
    logger.debug("phase chains for %s.%s -> %s", model, alias, out)
    return out


def _coerce_parent_kw(model: type, parent_kw: Dict[str, Any]) -> None:
    for name, val in list(parent_kw.items()):
        col = getattr(model, name, None)
        try:
            parent_kw[name] = col.type.python_type(val)  # type: ignore[attr-defined]
            logger.debug("coerced parent kw %s=%s", name, parent_kw[name])
        except Exception:
            logger.debug("failed coercing parent kw %s", name, exc_info=True)
