from sqlalchemy import String
from tigrbl_core._spec.storage_spec import StorageSpec

from tigrbl_base._base._column_base import ColumnBase
from tigrbl_base._base._table_base import TableBase


def test_table_base_tablename_resource_and_getitem() -> None:
    class User(TableBase):
        id = ColumnBase(storage=StorageSpec(type_=String, primary_key=True))
        name = ColumnBase(storage=StorageSpec(type_=String))

    user = User()
    user.name = "alice"

    assert User.__tablename__ == "user"
    assert User.resource_name == "user"
    assert user["name"] == "alice"
    assert User.metadata.naming_convention["pk"] == "pk_%(table_name)s"
