import pytest

from tigrbl import engine_ctx
from tigrbl import resolver as _resolver
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl._spec import FieldSpec as F, IOSpec as IO, StorageSpec as S
from tigrbl.shortcuts import acol
from tigrbl.table import Table
from tigrbl.types import Mapped, String


@pytest.mark.unit
def test_table_engine_ctx_auto_registers_provider() -> None:
    @engine_ctx(mem(async_=False))
    class Widget(Table, GUIDPk):
        __tablename__ = "widgets_engine_table"

        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )

    assert _resolver.resolve_provider(model=Widget) is None

    Widget.install_engines()
    provider = _resolver.resolve_provider(model=Widget)
    assert provider is not None
    assert provider.spec.kind == "sqlite"
    assert provider.spec.async_ is False


@pytest.mark.unit
def test_table_engine_ctx_on_instance_does_not_register() -> None:
    class Gadget(Table, GUIDPk):
        __tablename__ = "gadgets_engine_table"

        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read", "list")),
        )

    instance = Gadget()
    engine_ctx(mem(async_=False))(instance)

    assert _resolver.resolve_provider(model=Gadget) is None
