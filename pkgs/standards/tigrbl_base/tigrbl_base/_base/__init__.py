"""Base class implementations for tigrbl internals."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    "AppBase": "_app_base",
    "AliasBase": "_alias_base",
    "EngineBase": "_engine_base",
    "EngineProviderBase": "_engine_provider_base",
    "HookBase": "_hook_base",
    "ForeignKeyBase": "_storage",
    "OpBase": "_op_base",
    "RequestBase": "_request_base",
    "SchemaBase": "_schema_base",
    "SessionABC": "_session_abc",
    "TigrblSessionBase": "_session_base",
    "TableBase": "_table_base",
    "TableRegistryBase": "_table_registry_base",
}

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(f"{__name__}.{module_name}")
    value = getattr(module, name)
    globals()[name] = value
    return value
