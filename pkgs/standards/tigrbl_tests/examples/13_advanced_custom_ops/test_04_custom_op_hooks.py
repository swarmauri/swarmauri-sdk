from tigrbl import hook_ctx, op_ctx
from examples._support import build_simple_api, build_widget_model


def test_custom_op_hooks_register():
    """Test custom op hooks register."""
    Widget = build_widget_model("LessonCustomHook")

    @op_ctx(alias="report", target="custom", arity="collection")
    def report(cls, ctx):
        return [{"report": True}]

    @hook_ctx(ops="report", phase="POST_RESPONSE")
    def audit(cls, ctx):
        return None

    Widget.report = report
    Widget.audit = audit

    api = build_simple_api(Widget)
    api.bind(Widget)
    assert len(getattr(Widget.hooks, "report").POST_RESPONSE) == 1
