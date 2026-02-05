from tigrbl.column import S
from tigrbl.column.storage_spec import ForeignKey, ForeignKeySpec, StorageTransform


def test_storage_spec_defaults_and_fk():
    fk = ForeignKeySpec(target="tenants.id", on_delete="CASCADE")
    spec = S(type_=int, primary_key=True, fk=fk)
    assert spec.type_ is int
    assert spec.primary_key is True
    assert spec.fk is fk
    assert spec.nullable is None


def test_foreign_key_impl_inherits_spec():
    fk = ForeignKey(target="tenants.id", on_delete="CASCADE")
    assert isinstance(fk, ForeignKeySpec)
    assert fk.target == "tenants.id"
    assert fk.on_delete == "CASCADE"
    spec = S(type_=int, fk=fk)
    assert spec.fk is fk


def test_storage_spec_transform_settings():
    transform = StorageTransform(
        to_stored=lambda v, ctx: v, from_stored=lambda v, ctx: v
    )
    spec = S(type_=str, transform=transform, unique=True, index=True)
    assert spec.transform is transform
    assert spec.unique is True
    assert spec.index is True
