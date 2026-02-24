from __future__ import annotations

from tigrbl import Base, op_ctx


def test_op_ctx_registers_custom_alias() -> None:
    class Widget(Base):
        __tablename__ = "op_ctx_widgets"

        @op_ctx(alias="ping", target="custom", arity="collection")
        def ping(cls, ctx):
            return {"ok": True}

    assert hasattr(Widget, "__tigrbl_ops__")
