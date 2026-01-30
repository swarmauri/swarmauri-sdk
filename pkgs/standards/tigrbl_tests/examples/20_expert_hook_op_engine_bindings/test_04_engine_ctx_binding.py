from tigrbl import bind, engine_ctx

from examples._support import build_widget_model


def test_engine_ctx_binding_sets_op_and_table_config():
    @engine_ctx(kind="sqlite", mode="memory", async_=False)
    def ping(cls, ctx):
        return {"ok": True}

    Widget = build_widget_model("LessonEngineBinding", extra_attrs={"ping": ping})
    engine_ctx(kind="sqlite", mode="memory", async_=False)(Widget)

    bind(Widget)

    assert Widget.table_config["engine"]["kind"] == "sqlite"
    assert Widget.ping.__tigrbl_engine_ctx__["kind"] == "sqlite"
