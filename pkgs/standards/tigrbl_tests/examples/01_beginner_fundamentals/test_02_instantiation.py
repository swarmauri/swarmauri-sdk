from examples._support import build_widget_model


def test_model_instantiation_sets_attributes():
    Widget = build_widget_model("LessonInstance")
    widget = Widget(name="starter")
    assert widget.name == "starter"
