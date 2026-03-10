from __future__ import annotations

from tigrbl_core._spec.storage_spec import (
    ForeignKeySpec,
    StorageSpec,
    StorageTransformSpec,
)


def test_storage_transform_and_foreign_key_defaults() -> None:
    transform = StorageTransformSpec()
    fk = ForeignKeySpec(target="users.id")

    assert transform.to_stored is None
    assert transform.from_stored is None
    assert fk.on_delete == "RESTRICT"
    assert fk.match == "SIMPLE"


def test_storage_spec_field_assignment() -> None:
    spec = StorageSpec(
        type_=str, nullable=False, unique=True, fk=ForeignKeySpec("x.id")
    )

    assert spec.type_ is str
    assert spec.nullable is False
    assert spec.unique is True
    assert spec.fk is not None
    assert spec.fk.target == "x.id"
