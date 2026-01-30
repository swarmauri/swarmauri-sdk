from tigrbl import bind, hook_ctx

from examples._support import build_widget_model


def test_model_hook_binding_populates_phase_chain():
    @hook_ctx(ops="create", phase="POST_COMMIT")
    def notify(cls, ctx):
        return None

    Widget = build_widget_model("LessonHookBinding", extra_attrs={"notify": notify})

    bind(Widget)

    hooks = Widget.hooks.create.POST_COMMIT
    assert any(step.__name__ == "notify" for step in hooks)
