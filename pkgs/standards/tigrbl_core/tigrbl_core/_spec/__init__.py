"""Canonical spec package.

Keep this module import-light to avoid circular imports during package startup.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    "AliasSpec": "alias_spec",
    "AppSpec": "app_spec",
    "Binding": "binding_spec",
    "BindingRegistry": "binding_spec",
    "BindingSpec": "binding_spec",
    "HttpRestBindingSpec": "binding_spec",
    "HttpJsonRpcBindingSpec": "binding_spec",
    "WsBindingSpec": "binding_spec",
    "resolve_rest_nested_prefix": "binding_spec",
    "ColumnSpec": "column_spec",
    "EngineSpec": "engine_spec",
    "EngineProviderSpec": "engine_spec",
    "FieldSpec": "field_spec",
    "HookPhase": "hook_spec",
    "HookSpec": "hook_spec",
    "IOSpec": "io_spec",
    "MiddlewareSpec": "middleware_spec",
    "OpSpec": "op_spec",
    "Arity": "op_spec",
    "PersistPolicy": "op_spec",
    "TargetOp": "op_spec",
    "PHASE": "hook_types",
    "PHASES": "hook_types",
    "TemplateSpec": "response_spec",
    "ResponseSpec": "response_spec",
    "RequestSpec": "request_spec",
    "RouterSpec": "router_spec",
    "SchemaSpec": "schema_spec",
    "SchemaArg": "schema_spec",
    "SchemaRef": "schema_spec",
    "SessionSpec": "session_spec",
    "session_spec": "session_spec",
    "tx_read_committed": "session_spec",
    "tx_repeatable_read": "session_spec",
    "tx_serializable": "session_spec",
    "readonly": "session_spec",
    "wrap_sessionmaker": "session_spec",
    "StorageSpec": "storage_spec",
    "StorageTransform": "storage_spec",
    "ForeignKeySpec": "storage_spec",
    "TableSpec": "table_spec",
    "TableRegistrySpec": "table_registry_spec",
    "F": "shortcuts_spec",
    "IO": "shortcuts_spec",
    "S": "shortcuts_spec",
    "makeColumn": "shortcuts_spec",
    "makeVirtualColumn": "shortcuts_spec",
    "acol": "shortcuts_spec",
    "vcol": "shortcuts_spec",
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
