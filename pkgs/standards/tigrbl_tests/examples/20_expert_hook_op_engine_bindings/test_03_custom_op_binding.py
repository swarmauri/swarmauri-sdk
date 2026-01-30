from tigrbl import bind, op_ctx

from examples._support import build_widget_model


def test_custom_op_binding_registers_op():
    @op_ctx(alias="ping", target="custom", arity="collection")
    def ping(cls, ctx):
        return {"ok": True}

    Widget = build_widget_model("LessonOpBinding", extra_attrs={"ping": ping})

    specs = bind(Widget)

    assert any(spec.alias == "ping" and spec.target == "custom" for spec in specs)
