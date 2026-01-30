from tigrbl import alias_ctx
from examples._support import build_simple_api, build_widget_model, collect_aliases


def test_alias_ctx_registers_custom_name():
    """Test alias ctx registers custom name."""
    Widget = alias_ctx(read="lookup")(build_widget_model("LessonAlias"))

    api = build_simple_api(Widget)
    aliases = collect_aliases(api, Widget)
    assert "lookup" in aliases
