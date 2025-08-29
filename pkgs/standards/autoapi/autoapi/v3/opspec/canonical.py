from __future__ import annotations

from typing import Type

from ..config.constants import (
    AUTOAPI_DEFAULTS_EXCLUDE_ATTR,
    AUTOAPI_DEFAULTS_INCLUDE_ATTR,
    AUTOAPI_DEFAULTS_MODE_ATTR,
)

DEFAULT_CANON_VERBS = {
    "create",
    "read",
    "update",
    "replace",
    "upsert",
    "delete",
    "list",
    "clear",
}


def should_wire_canonical(table: Type, op: str) -> bool:
    mode = getattr(table, AUTOAPI_DEFAULTS_MODE_ATTR, "all")
    inc = set(getattr(table, AUTOAPI_DEFAULTS_INCLUDE_ATTR, set()))
    exc = set(getattr(table, AUTOAPI_DEFAULTS_EXCLUDE_ATTR, set()))
    if mode == "none":
        return False
    if mode == "some":
        return op in inc
    allowed = (DEFAULT_CANON_VERBS | inc) - exc
    return op in allowed  # mode == "all"
