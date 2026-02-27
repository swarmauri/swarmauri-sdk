from __future__ import annotations

from tigrbl.decorators import hook_ctx
from tigrbl.table import Base


def test_hook_ctx_registers_hook() -> None:
    class Widget(Base):
        __tablename__ = "hook_ctx_widgets"

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def record(cls, ctx):
            ctx["hooked"] = True

    hooks = getattr(Widget, "__tigrbl_hooks__", {})
    assert "create" in hooks
