from __future__ import annotations
from typing import Iterable, Literal, Type
from .table_config_provider import TableConfigProvider
from ..opspec import OpSpec
from ..config.constants import (
    AUTOAPI_DEFAULTS_EXCLUDE_ATTR,
    AUTOAPI_DEFAULTS_INCLUDE_ATTR,
    AUTOAPI_DEFAULTS_MODE_ATTR,
)


class OpConfigProvider(TableConfigProvider):
    __autoapi_ops__: Iterable[OpSpec] = ()

    # Default canonical verbs wiring policy
    __autoapi_defaults_mode__: Literal["all", "none", "some"] = "all"
    __autoapi_defaults_include__: set[str] = set()
    __autoapi_defaults_exclude__: set[str] = set()


DEFAULT_CANON_VERBS = {"create", "read", "update", "delete", "list", "clear"}


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
