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
    "MRO_COLLECTORS",
    "RESOLVERS",
    "INSTALLS",
    "collect",
    "install",
    "collect_engine_bindings",
    "install_engine_bindings",
    "install_from_objects",
]


def __getattr__(name: str):
    if name in {"bind", "rebind"}:
        return getattr(import_module(".model", __name__), name)
    if name == "build_schemas":
        return import_module(".schemas", __name__).build_and_attach
    if name == "build_hooks":
        return import_module(".hooks", __name__).build_and_attach
    if name == "build_handlers":
        return import_module(".handlers", __name__).build_and_attach
    if name == "register_rpc":
        return import_module(".rpc", __name__).register_and_attach
    if name == "build_rest":
        return import_module(".rest", __name__).build_router_and_attach
    if name == "bind_response":
        return import_module(".responses_resolver", __name__).resolve_response_spec
    if name in {"include_table", "include_tables"}:
        return getattr(import_module(".router.include", __name__), name)
    if name == "rpc_call":
        # ``tigrbl.mapping.rpc_call`` should execute an RPC op end-to-end and
        # return the serialized operation result.
        return getattr(import_module(".router.rpc", __name__), name)
    if name in {
        "INSTALLS",
        "MRO_COLLECTORS",
        "RESOLVERS",
        "collect",
        "install",
        "collect_engine_bindings",
        "install_engine_bindings",
        "install_from_objects",
    }:
        return getattr(import_module(".traversal", __name__), name)
    raise AttributeError(name)
