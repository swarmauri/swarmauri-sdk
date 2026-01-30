from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem

from examples._support import build_widget_model


def test_app_binding_includes_multiple_models():
    Widget = build_widget_model("LessonAppBulkWidget")
    Gadget = build_widget_model("LessonAppBulkGadget")
    app = TigrblApp(engine=mem(async_=False))

    app.include_models([Widget, Gadget])

    assert {Widget.__name__, Gadget.__name__}.issubset(app.models)
