from __future__ import annotations

from importlib import import_module

_MODULES = (
    "app",
    "column",
    "engine",
    "hook",
    "responses",
    "router",
    "schema",
    "table",
)

__all__ = list(_MODULES)


def __getattr__(name: str):
    for module_name in _MODULES:
        module = import_module(f"{__name__}.{module_name}")
        if hasattr(module, name):
            value = getattr(module, name)
            globals()[name] = value
            return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__ + [k for k in globals() if not k.startswith("_")])
