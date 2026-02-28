from types import SimpleNamespace

from sqlalchemy import Integer, String

from tigrbl.mapping import include_table
from tigrbl._spec import ColumnSpec, StorageSpec as S
from tigrbl import Table


class Widget(Table):
    __tablename__ = "widgets_columns_namespace"

    id: int = ColumnSpec(storage=S(type_=Integer, primary_key=True))
    name: str = ColumnSpec(storage=S(type_=String, nullable=False))


def test_include_model_coerces_columns_namespace() -> None:
    app = SimpleNamespace()

    include_table(app, Widget, mount_router=False)

    assert app.columns["Widget"] == ("id", "name")
