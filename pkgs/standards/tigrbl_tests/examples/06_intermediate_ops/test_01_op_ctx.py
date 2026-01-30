from tigrbl import op_ctx
from examples._support import build_simple_api, build_widget_model, collect_aliases


def test_custom_op_ctx_registers_alias():
    Widget = build_widget_model("LessonOp")

    @op_ctx(alias="search", target="custom", arity="collection")
    def search(cls, ctx):
        return [{"name": "found"}]

    Widget.search = search

    api = build_simple_api(Widget)
    aliases = collect_aliases(api, Widget)
    assert "search" in aliases
