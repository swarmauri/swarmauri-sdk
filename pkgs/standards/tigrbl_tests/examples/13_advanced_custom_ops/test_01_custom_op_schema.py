from tigrbl import op_ctx, SchemaRef
from examples._support import build_simple_api, build_widget_model, get_op_spec


def test_custom_op_declares_schema_refs():
    """Test custom op declares schema refs."""
    Widget = build_widget_model("LessonSchema")

    @op_ctx(
        alias="summarize",
        target="custom",
        arity="collection",
        request_schema=SchemaRef("create", "in"),
        response_schema=SchemaRef("read", "out"),
    )
    def summarize(cls, ctx):
        return [{"name": "summary"}]

    Widget.summarize = summarize

    api = build_simple_api(Widget)
    op = get_op_spec(api, Widget, "summarize")
    assert op.request_model is not None
