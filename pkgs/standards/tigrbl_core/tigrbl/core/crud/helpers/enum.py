from __future__ import annotations

from typing import Any, Mapping
import builtins as _builtins
import logging

from . import SAEnum

logger = logging.getLogger("uvicorn")


def _validate_enum_values(model: type, values: Mapping[str, Any]) -> None:
    logger.debug("_validate_enum_values called with model=%s values=%s", model, values)
    if not values or SAEnum is None:
        logger.debug("_validate_enum_values no validation needed")
        return

    table = getattr(model, "__table__", None)
    if table is None:
        return

    get = getattr(table.c, "get", None)

    for key, v in values.items():
        col = get(key) if get else None
        if col is None:
            try:
                col = table.c[key]  # type: ignore[index]
            except Exception:
                col = None
        if col is None:
            continue

        col_type = getattr(col, "type", None)
        if col_type is None or not isinstance(col_type, SAEnum):
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
