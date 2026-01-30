from tigrbl import TigrblApi
from tigrbl.engine.shortcuts import mem

from examples._support import build_widget_model


def test_api_binding_includes_multiple_models():
    Widget = build_widget_model("LessonApiBulkWidget")
    Gadget = build_widget_model("LessonApiBulkGadget")
    api = TigrblApi(engine=mem(async_=False))

    api.include_models([Widget, Gadget])

    assert {Widget.__name__, Gadget.__name__}.issubset(api.models)
