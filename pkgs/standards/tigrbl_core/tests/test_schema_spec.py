from __future__ import annotations

from tigrbl_core._spec.schema_spec import SchemaRef, SchemaSpec


def test_schema_spec_fields() -> None:
    spec = SchemaSpec(alias="public", kind="out", schema={"name": "Demo"})

    assert spec.alias == "public"
    assert spec.kind == "out"
    assert spec.schema == {"name": "Demo"}


def test_schema_ref_defaults() -> None:
    ref = SchemaRef(alias="create")

    assert ref.alias == "create"
    assert ref.kind == "in"
