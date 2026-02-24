from types import SimpleNamespace

from sqlalchemy import Integer, String

from tigrbl.bindings import include_table
from tigrbl.column import ColumnSpec, S
from tigrbl.table import Table


class Widget(Table):
    __tablename__ = "widgets_columns_namespace"

    id: int = ColumnSpec(storage=S(type_=Integer, primary_key=True))
    name: str = ColumnSpec(storage=S(type_=String, nullable=False))


def test_include_model_coerces_columns_namespace() -> None:
<<<<<<< HEAD
    app = SimpleNamespace()

    include_table(app, Widget, mount_router=False)

    assert app.columns["Widget"] == ("id", "name")
=======
    router = SimpleNamespace()

    include_model(router, Widget, mount_router=False)

    assert router.columns["Widget"] == ("id", "name")
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
