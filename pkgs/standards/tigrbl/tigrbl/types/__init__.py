"""Compatibility type exports for legacy ``tigrbl.types`` imports."""

from tigrbl.column import F, IO, S, acol
from tigrbl_typing import types as _typing_types
from tigrbl_typing.types import __all__ as _typing_all
from tigrbl_concrete.decorators import allow_anon

for _name in _typing_all:
    globals()[_name] = getattr(_typing_types, _name)

__all__ = [*_typing_all, "F", "IO", "S", "acol", "allow_anon"]
