from tigrbl import TigrblApi
from tigrbl.engine.shortcuts import mem

from examples._support import build_widget_model


def test_api_binding_attaches_namespaces():
    Widget = build_widget_model("LessonApiNamespaces")
    api = TigrblApi(engine=mem(async_=False))

    api.include_model(Widget)

    assert hasattr(api.schemas, Widget.__name__)
    assert hasattr(api.handlers, Widget.__name__)
