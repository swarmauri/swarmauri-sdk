from examples._support import build_simple_api, build_widget_model


def test_app_includes_model_and_registry():
    """Test app includes model and registry."""
    Widget = build_widget_model("LessonApi")
    api = build_simple_api(Widget)
    registry = api.registry(Widget)
    assert registry is not None
