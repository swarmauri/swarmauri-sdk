from __future__ import annotations

from tigrbl import Base, hook_ctx


def test_hook_ctx_registers_hook() -> None:
    class Widget(Base):
        __tablename__ = "hook_ctx_widgets"

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def record(cls, ctx):
            ctx["hooked"] = True

    hooks = getattr(Widget, "__tigrbl_hooks__", {})
    assert "create" in hooks
