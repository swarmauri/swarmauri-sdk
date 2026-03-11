"""Compatibility facade for ``tigrbl.mapping``.

Forward all mapping imports to ``tigrbl_canon.mapping`` while keeping the
legacy import surface (`tigrbl.mapping.*`) available during refactoring.
"""

from __future__ import annotations

from importlib import import_module
import sys
from types import ModuleType
from typing import Any

_CANON_PACKAGE = "tigrbl_canon.mapping"
_canon: ModuleType = import_module(_CANON_PACKAGE)

# Route submodule discovery (e.g. ``tigrbl.mapping.engine_resolver``) to the
# canonical mapping package.
__path__ = list(getattr(_canon, "__path__", []))

# Mirror canonical public exports when present.
__all__ = list(getattr(_canon, "__all__", ()))
for _name in __all__:
    globals()[_name] = getattr(_canon, _name)


def __getattr__(name: str) -> Any:
    try:
        return getattr(_canon, name)
    except AttributeError:
        module = import_module(f"{_CANON_PACKAGE}.{name}")
        sys.modules.setdefault(f"{__name__}.{name}", module)
        return module


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(dir(_canon)))
