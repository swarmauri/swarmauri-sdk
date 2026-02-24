from __future__ import annotations


def build_jsonrpc_router(*args, **kwargs):
    del args, kwargs
    raise RuntimeError("JSON-RPC transport dispatcher has been removed from ingress.")


__all__ = ["build_jsonrpc_router"]
