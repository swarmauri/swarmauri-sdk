from tigrbl import bind, rebind
from examples._support import build_widget_model


def test_bind_and_rebind_update_specs():
    Widget = build_widget_model("LessonBind")
    bind(Widget)
    initial = Widget.__tigrbl_cols__
    rebind(Widget)
    assert Widget.__tigrbl_cols__ == initial
