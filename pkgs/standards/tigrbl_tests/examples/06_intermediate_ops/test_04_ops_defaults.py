from examples._support import build_simple_api, build_widget_model, collect_aliases


def test_default_ops_include_list():
    """Test default ops include list."""
    Widget = build_widget_model("LessonDefaultOps")
    api = build_simple_api(Widget)
    aliases = collect_aliases(api, Widget)
    assert "list" in aliases
