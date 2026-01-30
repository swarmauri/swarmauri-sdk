from tigrbl import App, TigrblApi
from tigrbl.engine.shortcuts import mem

from examples._support import build_widget_model


def test_api_binding_mounts_diagnostics_router():
    Widget = build_widget_model("LessonApiDiagnostics")
    api = TigrblApi(engine=mem(async_=False))
    api.include_model(Widget)

    app = App()
    router = api.attach_diagnostics(app=app)

    assert router is not None
