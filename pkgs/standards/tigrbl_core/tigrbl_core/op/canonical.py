from __future__ import annotations

from typing import Type
from tigrbl_core.config.constants import (
    ALL_VERBS,
    TIGRBL_DEFAULTS_EXCLUDE_ATTR,
    TIGRBL_DEFAULTS_INCLUDE_ATTR,
    TIGRBL_DEFAULTS_MODE_ATTR,
)

DEFAULT_CANON_VERBS = {
    "create",
    "read",
    "update",
    "replace",
    "delete",
    "list",
    "clear",
}


def should_wire_canonical(table: Type, op: str) -> bool:
    helper = getattr(table, "should_wire_canonical", None)
    if callable(helper):
        return bool(helper(op))

    mode = getattr(table, TIGRBL_DEFAULTS_MODE_ATTR, "all")
    inc = set(getattr(table, TIGRBL_DEFAULTS_INCLUDE_ATTR, set()))
    exc = set(getattr(table, TIGRBL_DEFAULTS_EXCLUDE_ATTR, set()))

    if mode == "none":
        return False
    if mode == "some":
        return op in inc

    default_verbs = set(getattr(table, "DEFAULT_CANON_VERBS", DEFAULT_CANON_VERBS))
    default_verbs &= set(v for v in ALL_VERBS if v != "custom")
    allowed = (default_verbs | inc) - exc
    return op in allowed
