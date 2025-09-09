from __future__ import annotations
from typing import Iterable, Literal, Type
from .table_config_provider import TableConfigProvider
from ..ops.spec import OpSpec


class OpConfigProvider(TableConfigProvider):
    __tigrbl_ops__: Iterable[OpSpec] = ()

    # Default canonical verbs wiring policy
    __tigrbl_defaults_mode__: Literal["all", "none", "some"] = "all"
    __tigrbl_defaults_include__: set[str] = set()
    __tigrbl_defaults_exclude__: set[str] = set()


def should_wire_canonical(table: Type, op: str) -> bool:
    mode = getattr(table, "__tigrbl_defaults_mode__", "all")
    inc = getattr(table, "__tigrbl_defaults_include__", set())
    exc = getattr(table, "__tigrbl_defaults_exclude__", set())
    if mode == "none":
        return False
    if mode == "some":
        return op in inc
    return op not in exc  # mode == "all"
