from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem

from examples._support import build_widget_model


def test_app_binding_mounts_jsonrpc_router():
    Widget = build_widget_model("LessonAppJsonrpc")
    app = TigrblApp(engine=mem(async_=False))
    app.include_model(Widget)

    router = app.mount_jsonrpc()

    assert router is not None
