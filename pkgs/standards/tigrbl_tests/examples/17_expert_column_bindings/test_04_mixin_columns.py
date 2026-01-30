from tigrbl import bind

from examples._support import build_widget_model


def test_column_binding_includes_mixin_specs():
    Widget = build_widget_model("LessonColumnMixin", use_specs=True)

    bind(Widget)

    cols = Widget.__tigrbl_cols__
    assert cols["id"].storage.primary_key is True
