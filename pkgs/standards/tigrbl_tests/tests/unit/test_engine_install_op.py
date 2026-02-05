import pytest

from tigrbl import Op, TigrblApp, engine_ctx, op_ctx
from tigrbl.engine import resolver as _resolver
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.specs import F, IO, S, acol
from tigrbl.table import Table
from tigrbl.types import Mapped, String


@pytest.mark.unit
def test_op_spec_engine_auto_registers() -> None:
    class Widget(Table, GUIDPk):
        __tablename__ = "widgets_engine_op"

        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )

        ping = Op(
            alias="ping",
            target="custom",
            arity="collection",
            engine=mem(async_=True),
        )

    provider = _resolver.resolve_provider(model=Widget, op_alias="ping")
    assert provider is not None
    assert provider.spec.kind == "sqlite"
    assert provider.spec.async_ is True

    Widget.install_engines()
    provider = _resolver.resolve_provider(model=Widget, op_alias="ping")
    assert provider is not None
    assert provider.spec.async_ is True


@pytest.mark.unit
def test_op_ctx_engine_requires_install_engines_after_bind() -> None:
    class Gadget(Table, GUIDPk):
        __tablename__ = "gadgets_engine_op"

        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )

        @op_ctx(alias="ping", target="custom", arity="collection")
        @engine_ctx(mem(async_=True))
        def ping(cls, ctx):
            return {"ok": True, "ctx": ctx}

    app = TigrblApp(engine=mem(async_=False))
    app.include_model(Gadget)

    provider = _resolver.resolve_provider(model=Gadget, op_alias="ping")
    assert provider is not None
    assert provider.spec.async_ is False

    app.install_engines(models=(Gadget,))
    provider = _resolver.resolve_provider(model=Gadget, op_alias="ping")
    assert provider is not None
    assert provider.spec.async_ is False
