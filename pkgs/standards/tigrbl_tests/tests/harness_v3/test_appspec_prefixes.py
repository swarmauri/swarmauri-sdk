"""Harness: AppSpec-level configuration behavior.

These tests define the *contract* for AppSpec-derived apps:
- JSON-RPC is served under a configurable prefix.
- System endpoints are served under a configurable prefix.
- Documentation reflects those prefixes.

The implementation is free to change internally as long as these
externals remain stable.
"""

from __future__ import annotations

from tigrbl import TigrblApp
from tigrbl.system.docs.openrpc import build_openrpc_spec


def test_appspec_prefixes_materialize_on_app_instance() -> None:
    class MyApp(TigrblApp):
        JSONRPC_PREFIX = "/rpc-demo"
        SYSTEM_PREFIX = "/system-demo"

    app = MyApp()

    assert app.jsonrpc_prefix == "/rpc-demo"
    assert app.system_prefix == "/system-demo"


def test_openrpc_servers_uses_jsonrpc_prefix() -> None:
    class MyApp(TigrblApp):
        JSONRPC_PREFIX = "/rpc-demo"

    app = MyApp()

    spec = build_openrpc_spec(app)

    # Contract: OpenRPC advertises the JSON-RPC endpoint prefix.
    assert spec["servers"], "OpenRPC spec must declare at least one server"
    assert spec["servers"][0]["url"] == "/rpc-demo"


def test_mount_jsonrpc_sets_prefix_and_does_not_require_routes() -> None:
    """mount_jsonrpc is an API convenience; it must not rely on legacy route builders."""

    app = TigrblApp()

    # Contract: should not raise.
    app.mount_jsonrpc(prefix="/rpc-mounted")
    assert app.jsonrpc_prefix == "/rpc-mounted"

    # Idempotent.
    app.mount_jsonrpc(prefix="/rpc-mounted")
    assert app.jsonrpc_prefix == "/rpc-mounted"
