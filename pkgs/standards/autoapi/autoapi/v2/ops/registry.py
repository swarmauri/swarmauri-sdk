from __future__ import annotations
from typing import Iterable, Type
from .spec import OpSpec

_REGISTRY: dict[Type, list[OpSpec]] = {}

def register_ops(table: Type, specs: Iterable[OpSpec]) -> None:
    _REGISTRY.setdefault(table, []).extend(specs)

def get_registered_ops(table: Type) -> list[OpSpec]:
    return list(_REGISTRY.get(table, []))
