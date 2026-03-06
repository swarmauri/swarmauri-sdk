from __future__ import annotations

from importlib import import_module
from pkgutil import extend_path

_CANON = "tigrbl_canon.mapping"
_canon = import_module(_CANON)
__path__ = extend_path(__path__, __name__)
__path__.extend(list(getattr(_canon, "__path__", [])))

__all__ = [
    "bind",
    "rebind",
    "build_schemas",
    "build_hooks",
    "build_handlers",
    "register_rpc",
    "build_rest",
    "bind_response",
    "include_table",
    "include_tables",
    "rpc_call",
    "MRO_COLLECTORS",
    "RESOLVERS",
    "INSTALLS",
    "collect",
    "install",
    "collect_engine_bindings",
    "install_engine_bindings",
    "install_from_objects",
    "engine_resolver",
    "core_resolver",
    "config_resolver",
    "op_resolver",
    "app_mro_collect",
    "collect_decorated_schemas",
    "column_mro_collect",
    "hook_mro_collect",
    "op_mro_collect",
    "router_mro_collect",
]


def __getattr__(name: str):
    canon = import_module(_CANON)
    try:
        return getattr(canon, name)
    except AttributeError:
        if name in {
            "engine_resolver",
            "core_resolver",
            "config_resolver",
            "op_resolver",
        }:
            return import_module(f"{_CANON}.{name}")
        if name in {
            "app_mro_collect",
            "collect_decorated_schemas",
            "column_mro_collect",
            "hook_mro_collect",
            "op_mro_collect",
            "router_mro_collect",
        }:
            return import_module(f"{_CANON}.{name}")
        raise
