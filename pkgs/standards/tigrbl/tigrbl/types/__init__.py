"""Compatibility type exports for legacy ``tigrbl.types`` imports."""

from __future__ import annotations

from tigrbl.shortcuts.column import acol
from tigrbl_core._spec import F, IO, S
from tigrbl_concrete.decorators import allow_anon
from tigrbl_typing import types as _typing_types
from tigrbl_typing.types import __all__ as _typing_all

_DEPRECATED_NAMES = {
    "Router": "tigrbl",
    "Request": "tigrbl",
    "Body": "tigrbl.core.crud",
    "Depends": "tigrbl.security",
    "HTTPException": "tigrbl.runtime.status",
    "Response": "tigrbl",
}


for _name in _typing_all:
    globals()[_name] = getattr(_typing_types, _name)


__all__ = [*_typing_all, "F", "IO", "S", "acol", "allow_anon"]


def __getattr__(name: str):
    if name in _DEPRECATED_NAMES:
        module = _DEPRECATED_NAMES[name]
        raise AttributeError(
            f"tigrbl.types no longer exports '{name}'. "
            f"Import it from '{module}' instead."
        )
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
