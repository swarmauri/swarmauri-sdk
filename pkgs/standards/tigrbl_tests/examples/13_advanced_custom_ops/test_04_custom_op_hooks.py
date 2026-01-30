import asyncio
import inspect

from tigrbl import Base, TigrblApp, hook_ctx, op_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_custom_op_hooks_register():
    """Test custom op hooks register."""

    class LessonCustomHook(Base, GUIDPk):
        __tablename__ = "lessoncustomhooks"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonCustomHook

    @op_ctx(alias="report", target="custom", arity="collection")
    def report(cls, ctx):
        return [{"report": True}]

    @hook_ctx(ops="report", phase="POST_RESPONSE")
    def audit(cls, ctx):
        return None

    Widget.report = report
    Widget.audit = audit

    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Widget)
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(init_result)
        else:
            loop.create_task(init_result)
    api.bind(Widget)
    assert len(getattr(Widget.hooks, "report").POST_RESPONSE) == 1
