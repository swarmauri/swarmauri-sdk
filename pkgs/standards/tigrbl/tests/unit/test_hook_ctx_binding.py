from tigrbl.hook import hook_ctx
from tigrbl.bindings.model import bind
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


Base.metadata.clear()


class Widget(Base, GUIDPk):
    __tablename__ = "widgets"
    name = Column(String, nullable=False)

    @hook_ctx(ops="create", phase="PRE_HANDLER")
    async def flag(cls, ctx):
        pass


def test_hook_ctx_binds_to_create_pre_handler():
    bind(Widget)
    hooks = Widget.hooks.create.PRE_HANDLER
    assert any(callable(h) for h in hooks)


class Gadget(Base, GUIDPk):
    __tablename__ = "gadgets"
    name = Column(String, nullable=False)

    @hook_ctx(ops=("create", "delete"), phase="PRE_HANDLER")
    async def counter(cls, ctx):
        pass


def test_hook_ctx_binds_hook_to_multiple_ops():
    bind(Gadget)
    for alias in ("create", "delete"):
        hooks = getattr(getattr(Gadget.hooks, alias), "PRE_HANDLER")
        assert any(callable(h) for h in hooks)


class Gizmo(Base, GUIDPk):
    __tablename__ = "gizmos"
    name = Column(String, nullable=False)

    @hook_ctx(ops="*", phase="POST_COMMIT")
    async def tally(cls, ctx):
        pass


def test_hook_ctx_wildcard_binds_to_all_ops():
    bind(Gizmo)
    for alias in ("create", "delete"):
        hooks = getattr(getattr(Gizmo.hooks, alias), "POST_COMMIT")
        assert any(callable(h) for h in hooks)
