"""Lesson 19: JSON-RPC mounting on apps.

Apps expose a JSON-RPC router for programmatic access to operations. Keeping
the router on the app instance ensures a consistent integration point for
transport layers and documentation tools.
"""

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem

from examples._support import build_widget_model


def test_app_binding_mounts_jsonrpc_router():
    """mount_jsonrpc produces a router for JSON-RPC endpoints."""
    Widget = build_widget_model("LessonAppJsonrpc")
    app = TigrblApp(engine=mem(async_=False))
    app.include_model(Widget)

    router = app.mount_jsonrpc()

    assert router is not None


def test_app_jsonrpc_mount_uses_prefix_setting():
    """The JSON-RPC prefix is configurable on the app instance."""
    Widget = build_widget_model("LessonAppJsonrpcPrefix")
    app = TigrblApp(engine=mem(async_=False), jsonrpc_prefix="/rpc-app")
    app.include_model(Widget)

    router = app.mount_jsonrpc()

    assert router is not None
