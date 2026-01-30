from tigrbl import bind, build_handlers
from examples._support import build_widget_model


def test_build_handlers_returns_handlers():
    Widget = build_widget_model("LessonHandlers")
    specs = bind(Widget)
    build_handlers(Widget, specs)
    assert hasattr(Widget, "handlers")
