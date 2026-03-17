from tigrbl import TableBase, TigrblApp, bind, hook_ctx


def test_hook_ctx_registers_hook() -> None:
    class Widget(TableBase):
        __tablename__ = "hook_ctx_widgets"

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        async def record(cls, ctx):
            ctx["hooked"] = True

    app = TigrblApp()
    app.include_table(Widget)
    app.initialize()
    bind(Widget)

    hooks = Widget.hooks.create.PRE_HANDLER
    assert any(getattr(h, "__name__", "") == "record" for h in hooks)
