"""Lesson 20: custom operation bindings.

Custom operations are declared as methods with ``@op_ctx`` and stored on the
model namespace (``__tigrbl_ops__``) for discovery. This pattern is preferred
because it keeps bespoke operations co-located with the model definition.
"""

from tigrbl import bind, op_ctx

from examples._support import build_widget_model


def test_custom_op_binding_registers_op():
    """Custom operations should appear in the bound OpSpec list."""

    @op_ctx(alias="ping", target="custom", arity="collection")
    def ping(cls, ctx):
        return {"ok": True}

    Widget = build_widget_model("LessonOpBinding", extra_attrs={"ping": ping})

    specs = bind(Widget)

    assert any(spec.alias == "ping" and spec.target == "custom" for spec in specs)


def test_custom_op_binding_populates_model_registry():
    """Custom op declarations stay attached to the classmethod."""

    @op_ctx(alias="healthcheck", target="custom", arity="collection")
    def healthcheck(cls, ctx):
        return {"ok": True}

    Widget = build_widget_model(
        "LessonOpBindingRegistry", extra_attrs={"healthcheck": healthcheck}
    )

    bind(Widget)

    assert hasattr(Widget.healthcheck, "__tigrbl_op_decl__")
