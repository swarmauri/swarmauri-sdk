from tigrbl import hook_ctx
from examples._support import build_simple_api, build_widget_model


def test_hook_scopes_apply_to_specific_ops():
    @hook_ctx(ops=("read", "update"), phase="POST_RESPONSE")
    def audit(cls, ctx):
        return None

    Widget = build_widget_model("LessonHookScope", extra_attrs={"audit": audit})

    api = build_simple_api(Widget)
    api.bind(Widget)
    read_hooks = Widget.__tigrbl_hooks__["read"]["POST_RESPONSE"]
    update_hooks = Widget.__tigrbl_hooks__["update"]["POST_RESPONSE"]
    assert len(read_hooks) == 1
    assert len(update_hooks) == 1
