from __future__ import annotations
from typing import Iterable, Literal, Type
from .table_config_provider import TableConfigProvider
from ..opspec import OpSpec
from ..config.constants import (
    DEFAULTS_MODE_ATTR,
    DEFAULTS_INCLUDE_ATTR,
    DEFAULTS_EXCLUDE_ATTR,
)


class OpConfigProvider(TableConfigProvider):
    __autoapi_ops__: Iterable[OpSpec] = ()

    # Default canonical verbs wiring policy
    __autoapi_defaults_mode__: Literal["all", "none", "some"] = "all"
    __autoapi_defaults_include__: set[str] = set()
    __autoapi_defaults_exclude__: set[str] = set()


def should_wire_canonical(table: Type, op: str) -> bool:
    mode = getattr(table, DEFAULTS_MODE_ATTR, "all")
    inc = getattr(table, DEFAULTS_INCLUDE_ATTR, set())
    exc = getattr(table, DEFAULTS_EXCLUDE_ATTR, set())
    if mode == "none":
        return False
    if mode == "some":
        return op in inc
    return op not in exc  # mode == "all"
