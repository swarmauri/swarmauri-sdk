from tigrbl import TigrblApi
from tigrbl.engine.shortcuts import mem

from examples._support import build_widget_model


def test_api_binding_mounts_jsonrpc_router():
    Widget = build_widget_model("LessonApiJsonrpc")
    api = TigrblApi(engine=mem(async_=False))
    api.include_model(Widget)

    router = api.mount_jsonrpc()

    assert router is not None
