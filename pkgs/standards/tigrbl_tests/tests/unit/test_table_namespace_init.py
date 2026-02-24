from types import SimpleNamespace

from tigrbl.specs import F, S, acol
from tigrbl.table import Table
from tigrbl.types import Integer, Mapped


class Widget(Table):
    __tablename__ = "widgets_namespace_init"

    id: Mapped[int] = acol(
        storage=S(type_=Integer, primary_key=True), field=F(py_type=int)
    )


def test_table_initializes_model_namespaces() -> None:
    assert isinstance(Widget.ops, SimpleNamespace)
    assert Widget.ops is Widget.opspecs
    assert isinstance(Widget.schemas, SimpleNamespace)
    assert isinstance(Widget.hooks, SimpleNamespace)
    assert isinstance(Widget.handlers, SimpleNamespace)
    assert isinstance(Widget.rpc, SimpleNamespace)
    assert isinstance(Widget.rest, SimpleNamespace)
    assert hasattr(Widget.rest, "router")
    assert isinstance(Widget.__tigrbl_hooks__, dict)
    assert isinstance(Widget.columns, SimpleNamespace)
    assert Widget.columns.id is Widget.__tigrbl_cols__["id"]
