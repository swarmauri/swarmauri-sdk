from tigrbl_base._base._storage import ForeignKeyBase
from tigrbl_core._spec.storage_spec import ForeignKeySpec


def test_foreign_key_base_inheritance_and_fields() -> None:
    fk = ForeignKeyBase(target="users(id)", on_delete="CASCADE")

    assert isinstance(fk, ForeignKeySpec)
    assert fk.target == "users(id)"
    assert fk.on_delete == "CASCADE"
