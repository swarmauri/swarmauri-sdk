from __future__ import annotations

from tigrbl_core._spec.field_spec import FieldSpec, ValidationInfo


def test_field_spec_defaults_and_constraints() -> None:
    spec = FieldSpec()

    assert spec.constraints == {}
    assert spec.required_in == ()
    assert spec.allow_null_in == ()


def test_validation_info_payload_fields() -> None:
    info = ValidationInfo(data={"a": 1}, field_name="name", mode="before")

    assert info.data == {"a": 1}
    assert info.field_name == "name"
    assert info.mode == "before"
