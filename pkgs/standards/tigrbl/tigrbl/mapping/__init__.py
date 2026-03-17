"""Facade: ``tigrbl.mapping`` wired to base/concrete owned binders."""

from __future__ import annotations

from importlib import import_module

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
    "collect",
    "install",
    "collect_engine_bindings",
    "install_engine_bindings",
    "install_from_objects",
    "app_mro_collect",
    "collect_decorated_schemas",
    "column_mro_collect",
    "hook_mro_collect",
    "op_mro_collect",
    "router_mro_collect",
]


def __getattr__(name: str):
    if name in {"bind", "rebind"}:
        return getattr(import_module("tigrbl_concrete._mapping.model"), name)
    if name == "build_schemas":
        return import_module("tigrbl_concrete._mapping.model")._materialize_schemas
    if name == "build_hooks":
        return import_module("tigrbl_concrete._mapping.model")._bind_model_hooks
    if name == "build_handlers":
        return import_module("tigrbl_concrete._mapping.model")._materialize_handlers
    if name == "register_rpc":
        return import_module("tigrbl_base._base._rpc_map").register_and_attach
    if name == "build_rest":

        def _build_rest(*args, **kwargs):
            if "router" not in kwargs:
                kwargs["router"] = None
            return import_module(
                "tigrbl_concrete._mapping.model"
            )._materialize_rest_router(*args, **kwargs)

        return _build_rest
    if name == "bind_response":
        return import_module(".responses_resolver", __name__).resolve_response_spec
    if name in {"include_table", "include_tables"}:
        return getattr(import_module("tigrbl_concrete._mapping.router.include"), name)
    if name == "rpc_call":
        return import_module("tigrbl_concrete._mapping.router.rpc").rpc_call
    if name in {
        "collect",
        "install",
        "collect_engine_bindings",
        "install_from_objects",
    }:
        return getattr(import_module("tigrbl.engine.bind"), name)
    if name == "install_engine_bindings":
        return import_module("tigrbl.engine.bind").install
    if name in {
        "app_mro_collect",
        "collect_decorated_schemas",
        "column_mro_collect",
        "hook_mro_collect",
        "op_mro_collect",
        "router_mro_collect",
    }:
        return import_module(f".{name}", __name__)
    raise AttributeError(name)
