from __future__ import annotations

from functools import lru_cache
from typing import Any, Mapping
import builtins as _builtins
import logging

from . import SAEnum

logger = logging.getLogger("uvicorn")


@lru_cache(maxsize=512)
def _enum_columns(model: type) -> dict[str, Any]:
    table = getattr(model, "__table__", None)
    if table is None:
        return {}
    columns = getattr(table, "c", None)
    if columns is None:
        return {}
    out: dict[str, Any] = {}
    for col in columns:
        col_type = getattr(col, "type", None)
        if col_type is not None and isinstance(col_type, SAEnum):
            name = getattr(col, "name", None)
            if isinstance(name, str) and name:
                out[name] = col_type
    return out


def _validate_enum_values(model: type, values: Mapping[str, Any]) -> None:
    logger.debug("_validate_enum_values called with model=%s values=%s", model, values)
    if not values or SAEnum is None:
        logger.debug("_validate_enum_values no validation needed")
        return

    enum_columns = _enum_columns(model)
    if not enum_columns:
        return

    for key, v in values.items():
        col_type = enum_columns.get(key)
        if col_type is None:
            continue

        if v is None:
            continue

        enum_cls = getattr(col_type, "enum_class", None)
        if enum_cls is not None:
            try:
                import enum as _enum
            except Exception:  # pragma: no cover
                _enum = None

            if _enum is not None and isinstance(v, _enum.Enum):
                if isinstance(v, enum_cls):
                    continue
                logger.debug(
                    "_validate_enum_values invalid value %s for enum %s", v, enum_cls
                )
                raise LookupError(
                    f"{v!r} is not among the defined enum values. "
                    f"Enum name: {enum_cls.__name__}. "
                    f"Possible values: {', '.join([e.value for e in enum_cls])}"
                )

            allowed_values = [e.value for e in enum_cls]
            allowed_names = [e.name for e in enum_cls]
            if isinstance(v, str) and (v in allowed_values or v in allowed_names):
                continue

            logger.debug(
                "_validate_enum_values invalid value %s for enum %s", v, enum_cls
            )
            raise LookupError(
                f"{v!r} is not among the defined enum values. "
                f"Enum name: {enum_cls.__name__}. "
                f"Possible values: {', '.join(allowed_values)}"
            )
        else:
            allowed = _builtins.list(getattr(col_type, "enums", []) or [])
            if isinstance(v, str) and v in allowed:
                continue
            logger.debug(
                "_validate_enum_values invalid value %s for enum %s", v, col_type
            )
            raise LookupError(
                f"{v!r} is not among the defined enum values. "
                f"Enum name: {getattr(col_type, 'name', 'Enum')}. "
                f"Possible values: {', '.join(allowed) if allowed else '(none)'}"
            )
    logger.debug("_validate_enum_values completed")
