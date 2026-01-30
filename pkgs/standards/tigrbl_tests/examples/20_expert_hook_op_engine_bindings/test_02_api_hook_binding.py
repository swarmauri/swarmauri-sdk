from tigrbl import TigrblApi
from tigrbl.engine.shortcuts import mem

from examples._support import build_widget_model


def test_api_hook_binding_merges_into_model():
    def audit(cls, ctx):
        return None

    api_hooks = {"*": {"PRE_HANDLER": [audit]}}
    api = TigrblApi(engine=mem(async_=False), api_hooks=api_hooks)
    Widget = build_widget_model("LessonApiHookBinding")

    api.include_model(Widget)

    hooks = Widget.hooks.create.PRE_HANDLER
    assert any(step.__name__ == "audit" for step in hooks)
