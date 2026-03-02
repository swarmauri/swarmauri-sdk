from __future__ import annotations

from tigrbl import TigrblApp


def _build_app() -> TigrblApp:
    app = TigrblApp()
    app.mount_jsonrpc(prefix="/rpc")
    return app


def test_rpc_options_jsonrpc_prefix_defaults_to_rpc() -> None:
    app = _build_app()
    assert app.jsonrpc_prefix == "/rpc"
    assert app.rpc_prefix == "/rpc"


def test_rpc_options_mount_jsonrpc_initializes_rpc_namespace() -> None:
    app = _build_app()
    assert hasattr(app, "rpc")
    assert app.rpc is not None
