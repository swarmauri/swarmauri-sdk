from types import SimpleNamespace

from sqlalchemy import Integer, String

from tigrbl.bindings import include_model
from tigrbl.column import ColumnSpec, S
from tigrbl.table import Table


class Widget(Table):
    __tablename__ = "widgets_columns_namespace"

    id: int = ColumnSpec(storage=S(type_=Integer, primary_key=True))
    name: str = ColumnSpec(storage=S(type_=String, nullable=False))


def test_include_model_coerces_columns_namespace() -> None:
    router = SimpleNamespace()

    include_model(router, Widget, mount_router=False)

    assert router.columns["Widget"] == ("id", "name")
