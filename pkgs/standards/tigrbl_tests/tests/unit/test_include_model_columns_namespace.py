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
    api = SimpleNamespace()

    include_model(api, Widget, mount_router=False)

    assert api.columns["Widget"] == ("id", "name")
