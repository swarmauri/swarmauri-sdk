"""RPC method decorator shim for gateway submodules."""

from .. import _rpc_dispatcher


def method(name: str):
    """Delegate to the gateway's dispatcher."""

    return _rpc_dispatcher.method(name)
