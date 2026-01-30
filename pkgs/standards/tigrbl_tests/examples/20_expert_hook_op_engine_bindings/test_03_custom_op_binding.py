"""Lesson 20: custom operation bindings.

Custom operations are declared as methods with ``@op_ctx`` and stored on the
model namespace (``__tigrbl_ops__``) for discovery. This pattern is preferred
because it keeps bespoke operations co-located with the model definition.
"""

from tigrbl import Base, bind, op_ctx
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_custom_op_binding_registers_op():
    """Custom operations should appear in the bound OpSpec list."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_op_binding"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

        @op_ctx(alias="ping", target="custom", arity="collection")
        def ping(cls, ctx):
            return {"ok": True}

    specs = bind(Widget)

    assert any(spec.alias == "ping" and spec.target == "custom" for spec in specs)


def test_custom_op_binding_populates_model_registry():
    """Custom op declarations stay attached to the classmethod."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_op_binding_registry"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

        @op_ctx(alias="healthcheck", target="custom", arity="collection")
        def healthcheck(cls, ctx):
            return {"ok": True}

    bind(Widget)

    assert hasattr(Widget.healthcheck, "__tigrbl_op_decl__")
