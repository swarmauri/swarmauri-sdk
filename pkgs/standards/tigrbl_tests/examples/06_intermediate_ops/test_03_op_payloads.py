from tigrbl import op_ctx
from examples._support import build_simple_api, build_widget_model, get_op_spec


def test_custom_op_returns_payload():
    """Test custom op returns payload."""
    Widget = build_widget_model("LessonPayload")

    @op_ctx(alias="summary", target="custom", arity="instance")
    def summary(cls, ctx):
        return {"status": "ok"}

    Widget.summary = summary

    api = build_simple_api(Widget)
    spec = get_op_spec(api, Widget, "summary")
    assert spec.handler is not None
