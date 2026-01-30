"""Lesson 18: JSON-RPC mounting on APIs.

This lesson shows how the API exposes a JSON-RPC router that can be mounted on
an application. Keeping the router attached to the API instance is the
preferred pattern because it preserves routing metadata alongside model
configuration.
"""

from tigrbl import TigrblApi
from tigrbl.engine.shortcuts import mem

from examples._support import build_widget_model


def test_api_binding_mounts_jsonrpc_router():
    """mount_jsonrpc returns a router ready to be attached to an app."""
    Widget = build_widget_model("LessonApiJsonrpc")
    api = TigrblApi(engine=mem(async_=False))
    api.include_model(Widget)

    router = api.mount_jsonrpc()

    assert router is not None


def test_jsonrpc_mount_uses_configured_prefix():
    """The JSON-RPC prefix on the API should be configurable."""
    Widget = build_widget_model("LessonApiJsonrpcPrefix")
    api = TigrblApi(engine=mem(async_=False), jsonrpc_prefix="/rpc-demo")
    api.include_model(Widget)

    router = api.mount_jsonrpc()

    assert router is not None
