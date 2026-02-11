from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping
import logging

logger = logging.getLogger(__name__)

# Optional imports – code must run even if these packages aren’t installed.
try:
    from pydantic import ValidationError as PydanticValidationError  # v2
except Exception:  # pragma: no cover
    PydanticValidationError = None  # type: ignore

RequestValidationError = None

try:
    # SQLAlchemy v1/v2 exception sets
    from sqlalchemy.exc import IntegrityError, DBAPIError, OperationalError
    from sqlalchemy.orm.exc import NoResultFound  # type: ignore
except Exception:  # pragma: no cover
    IntegrityError = DBAPIError = OperationalError = NoResultFound = None  # type: ignore


# Detect asyncpg constraint errors without importing asyncpg (optional dep).
_ASYNCPG_CONSTRAINT_NAMES = {
    "UniqueViolationError",
    "ForeignKeyViolationError",
    "NotNullViolationError",
    "CheckViolationError",
    "ExclusionViolationError",
}


def _is_asyncpg_constraint_error(exc: BaseException) -> bool:
    cls = type(exc)
    return (cls.__module__ or "").startswith("asyncpg") and (
        cls.__name__ in _ASYNCPG_CONSTRAINT_NAMES
    )


def _limit(s: str, n: int = 4000) -> str:
    return s if len(s) <= n else s[: n - 3] + "..."


def _stringify_exc(exc: BaseException) -> str:
    detail = getattr(exc, "detail", None)
    if detail:
        return _limit(str(detail))
    return _limit(f"{exc.__class__!r}: {str(exc) or repr(exc)}")


def _format_validation(err: Any) -> Any:
    try:
        items = err.errors()  # pydantic-style validation payload
        if isinstance(items, Iterable):
            return list(items)
    except Exception:  # pragma: no cover
        pass
    return _limit(str(err))


def _get_temp(ctx: Any) -> Mapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    return tmp if isinstance(tmp, Mapping) else {}


def _has_in_errors(ctx: Any) -> bool:
    tmp = _get_temp(ctx)
    if tmp.get("in_invalid") is True:
        return True
    errs = tmp.get("in_errors")
    return isinstance(errs, (list, tuple)) and len(errs) > 0


def _read_in_errors(ctx: Any) -> List[Dict[str, Any]]:
    tmp = _get_temp(ctx)
    errs = tmp.get("in_errors")
    if isinstance(errs, list):
        norm: List[Dict[str, Any]] = []
        for e in errs:
            if isinstance(e, Mapping):
                field = e.get("field")
                code = e.get("code") or "invalid"
                msg = e.get("message") or "Invalid value."
                entry = {"field": field, "code": code, "message": msg}
                for k, v in e.items():
                    if k not in entry:
                        entry[k] = v
                norm.append(entry)
        return norm
    return []


__all__ = [
    "PydanticValidationError",
    "RequestValidationError",
    "IntegrityError",
    "DBAPIError",
    "OperationalError",
    "NoResultFound",
    "_is_asyncpg_constraint_error",
    "_limit",
    "_stringify_exc",
    "_format_validation",
    "_get_temp",
    "_has_in_errors",
    "_read_in_errors",
]
