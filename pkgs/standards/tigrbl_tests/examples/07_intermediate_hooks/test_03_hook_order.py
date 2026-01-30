from tigrbl import hook_ctx
from examples._support import build_simple_api, build_widget_model


def test_hook_order_collects_multiple_hooks():
    @hook_ctx(ops="create", phase="PRE_HANDLER")
    def first(cls, ctx):
        return None

    @hook_ctx(ops="create", phase="PRE_HANDLER")
    def second(cls, ctx):
        return None

    Widget = build_widget_model(
        "LessonHookOrder",
        extra_attrs={"first": first, "second": second},
    )

    api = build_simple_api(Widget)
    api.bind(Widget)
    hooks = Widget.__tigrbl_hooks__["create"]["PRE_HANDLER"]
    assert len(hooks) == 2
