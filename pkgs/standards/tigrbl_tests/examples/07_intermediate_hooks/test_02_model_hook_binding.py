from tigrbl import hook_ctx
from examples._support import build_simple_api, build_widget_model


def test_model_hooks_bind_on_rebind():
    @hook_ctx(ops="create", phase="POST_COMMIT")
    def notify(cls, ctx):
        return None

    Widget = build_widget_model("LessonHook", extra_attrs={"notify": notify})

    api = build_simple_api(Widget)
    api.bind(Widget)
    hooks = Widget.__tigrbl_hooks__["create"]["POST_COMMIT"]
    assert len(hooks) == 1
