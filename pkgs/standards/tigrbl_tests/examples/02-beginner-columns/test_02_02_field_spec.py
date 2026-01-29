from __future__ import annotations

from tigrbl.specs import F


def test_field_spec_basics() -> None:
    spec = F(py_type=str, required_in=("create",), constraints={"min_length": 1})
    assert spec.py_type is str
    assert spec.required_in == ("create",)
    assert spec.constraints["min_length"] == 1
