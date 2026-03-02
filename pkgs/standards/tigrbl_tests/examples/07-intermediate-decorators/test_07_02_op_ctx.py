from __future__ import annotations

from tigrbl.decorators import op_ctx
from tigrbl import TableBase


def test_op_ctx_registers_custom_alias() -> None:
    class Widget(TableBase):
        __tablename__ = "op_ctx_widgets"

        @op_ctx(alias="ping", target="custom", arity="collection")
        def ping(cls, ctx):
            return {"ok": True}

    assert hasattr(Widget, "__tigrbl_ops__")
