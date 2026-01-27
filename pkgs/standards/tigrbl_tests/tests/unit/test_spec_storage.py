from tigrbl.column import S
from tigrbl.column.storage_spec import ForeignKeySpec, StorageTransform


def test_storage_spec_defaults_and_fk():
    fk = ForeignKeySpec(target="tenants.id", on_delete="CASCADE")
    spec = S(type_=int, primary_key=True, fk=fk)
    assert spec.type_ is int
    assert spec.primary_key is True
    assert spec.fk is fk
    assert spec.nullable is None


def test_storage_spec_transform_settings():
    transform = StorageTransform(
        to_stored=lambda v, ctx: v, from_stored=lambda v, ctx: v
    )
    spec = S(type_=str, transform=transform, unique=True, index=True)
    assert spec.transform is transform
    assert spec.unique is True
    assert spec.index is True
