import inspect

from tigrbl import Base, TigrblApp, hook_ctx, op_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_custom_op_hooks_register():
    """Test custom op hooks register."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_custom_hook"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

        @op_ctx(alias="report", target="custom", arity="collection")
        def report(cls, ctx):
            return [{"report": True}]

        @hook_ctx(ops="report", phase="POST_RESPONSE")
        def audit(cls, ctx):
            return None

<<<<<<< HEAD
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    init_result = app.initialize()
=======
    router = TigrblApp(engine=mem(async_=False))
    router.include_model(Widget)
    init_result = router.initialize()
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
    if inspect.isawaitable(init_result):
        import asyncio

        asyncio.run(init_result)
<<<<<<< HEAD
    app.bind(Widget)
=======
    router.bind(Widget)
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
    assert len(getattr(Widget.hooks, "report").POST_RESPONSE) == 1
