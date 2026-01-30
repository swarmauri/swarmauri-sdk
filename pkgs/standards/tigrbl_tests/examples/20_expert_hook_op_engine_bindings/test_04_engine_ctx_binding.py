"""Lesson 20: engine context bindings.

Engine context decorators attach engine metadata to models and methods. This
pattern is preferred because it keeps engine configuration discoverable from
the class namespace and ensures per-method overrides remain explicit.
"""

from tigrbl import bind, engine_ctx

from examples._support import build_widget_model


def test_engine_ctx_binding_sets_op_and_table_config():
    """Engine metadata should populate both model and method namespaces."""

    @engine_ctx(kind="sqlite", mode="memory", async_=False)
    def ping(cls, ctx):
        return {"ok": True}

    Widget = build_widget_model("LessonEngineBinding", extra_attrs={"ping": ping})
    engine_ctx(kind="sqlite", mode="memory", async_=False)(Widget)

    bind(Widget)

    assert Widget.table_config["engine"]["kind"] == "sqlite"
    assert Widget.ping.__tigrbl_engine_ctx__["kind"] == "sqlite"


def test_engine_ctx_binding_preserves_method_metadata():
    """The engine context should remain attached to the decorated callable."""

    @engine_ctx(kind="sqlite", mode="memory", async_=False)
    def audit(cls, ctx):
        return {"ok": True}

    Widget = build_widget_model(
        "LessonEngineBindingMethod", extra_attrs={"audit": audit}
    )
    engine_ctx(kind="sqlite", mode="memory", async_=False)(Widget)

    bind(Widget)

    assert Widget.audit.__tigrbl_engine_ctx__["mode"] == "memory"
